"""Focused issue-triage lab with measured scores and live neural outputs."""
import json
import math
from pathlib import Path

import pandas as pd
import streamlit as st

from src.app.resources import load_cnn_model, load_ir_and_nb_models
from src.common.config import CURATED_DATA_DIR
from src.ml.inference import predict_issue
from src.ml.train import fingerprint

EXAMPLES = {
    'Bug': ('Application crashes when opening settings', 'A null pointer exception stops the process on startup.'),
    'Feature': ('Add export to CSV', 'Please add a button to export the results to a CSV file.'),
    'Documentation': ('Update installation instructions in README', 'The documentation is missing a setup example.'),
    'Question': ('How can I configure the server?', 'Could someone explain which configuration options I should use?'),
}


def set_example(name: str) -> None:
    """Keep input widget keys in sync with the selected example."""
    st.session_state['issue_title'], st.session_state['issue_body'] = EXAMPLES[name]


@st.cache_data
def load_report() -> dict:
    """Accept scores only when model, vocabulary, and dataset match the report."""
    path = CURATED_DATA_DIR/'dl_report.json'
    if not path.exists():
        return {}
    report = json.loads(path.read_text(encoding='utf-8'))
    for name, digest in report['artifacts'].items():
        if fingerprint(CURATED_DATA_DIR/name) != digest:
            raise ValueError('The evaluation report is stale. Run python -m src.ml.train again.')
    return report


def show_scorecard(report: dict) -> None:
    """Compare measured held-out performance, including a majority-only baseline."""
    st.caption(f"Measured on {report['split_counts']['test']:,} held-out issues · best validation epoch {report['selected_epoch']}")
    cols = st.columns(4)
    cols[0].metric('CNN accuracy', f"{report['cnn']['accuracy']:.1%}")
    cols[1].metric('CNN macro-F1', f"{report['cnn']['macro_f1']:.1%}")
    cols[2].metric('Naive Bayes accuracy', f"{report['naive_bayes']['accuracy']:.1%}")
    cols[3].metric('Majority-only accuracy', f"{report['majority']['accuracy']:.1%}")
    st.caption('Accuracy = fraction correct. Macro-F1 = average class score, giving rare categories equal weight.')


def show_prediction(result: dict, nb, text: str) -> None:
    """Display every output class and the captured model shapes."""
    left, right = st.columns([3, 2])
    with left, st.container(border=True):
        st.subheader(f"Suggested label: {result['prediction']}")
        st.caption(f"CPU forward pass: {result['latency_ms']:.2f} ms · includes trace capture")
        scores = nb.predict_log_proba(text) if nb else {}
        offset = max(scores.values()) if scores else 0
        total = sum(math.exp(v-offset) for v in scores.values())
        frame = pd.DataFrame({'CNN': result['probabilities'],
                              'Naive Bayes': {k: math.exp(v-offset)/total for k,v in scores.items()}})
        st.bar_chart(frame, color=['#46c6ef','#9483ff'], horizontal=True, x_label='Model probability', y_label='Category')
        st.caption('These are model scores, not guaranteed correctness. Examples may be misclassified.')
    with right, st.container(border=True):
        st.markdown('#### What the network saw')
        st.write(f"Known words: {result['known_tokens']} · Unknown words: {result['unknown_tokens']}")
        if result['truncated']:
            st.warning('Only the first 50 processed words were used. Later text was truncated.')
        if result['unknown_tokens']:
            st.info('Unknown words become the same <unk> token, so meaning may be lost.')
        st.code('Input: '+str(result['input_shape'])+'\n'+'\n'.join(f'{k}: {v}' for k,v in result['trace'].items()), language='text')
    with st.expander('Inspect word IDs from this prediction'):
        st.dataframe(pd.DataFrame({'Word':result['tokens'], 'ID':result['token_ids'][:len(result['tokens'])]}), hide_index=True)


def show_evaluation(report: dict) -> None:
    """Plot logged training evidence and reveal failures by class."""
    with st.expander('Measured training curves & evaluation details'):
        history = pd.DataFrame(report['history']).set_index('epoch')
        st.line_chart(history[['train_loss','val_loss']], color=['#46c6ef','#9483ff'], x_label='Epoch', y_label='Cross-entropy loss')
        a = pd.DataFrame(report['no_dropout_history']).set_index('epoch')
        st.line_chart(pd.DataFrame({'Dropout 0.2':history['val_loss'], 'No dropout':a['val_loss']}),
                      color=['#46c6ef','#f6bf6a'], x_label='Epoch', y_label='Validation loss')
        st.caption('Same split, initialization, Adam settings, and epoch budget. Dropout helps only if the measured results support it; it does not guarantee an improvement.')
        st.markdown('**Per-class CNN results**')
        st.dataframe(pd.DataFrame(report['cnn']['per_class']).T, width='stretch')
        st.markdown('**Confusion matrix — rows: true class; columns: predicted class**')
        st.dataframe(pd.DataFrame(report['cnn']['confusion_matrix'], index=report['labels'], columns=report['labels']), width='stretch')
        st.caption(f"Train / validation / test: {report['split_counts']}. Duplicate issue identities and processed input sequences were removed before splitting. Repositories can still occur in multiple groups.")


def render() -> None:
    """Render a compact lab-ready demonstration with no fabricated evidence."""
    st.subheader('Deep learning / GitHub issue triage')
    st.write('A small text classifier suggests bug, enhancement, documentation, or question from an issue title and description.')
    model, vocab = load_cnn_model()
    if model is None or vocab is None:
        st.warning('Trained weights or vocabulary are missing. Run python -m src.ml.train to create them.')
        return
    report = load_report()
    if report:
        show_scorecard(report)
    else:
        st.info('No measured evaluation report is available for these weights.')
    if 'issue_title' not in st.session_state:
        set_example('Bug')
    with st.container(border=True):
        st.markdown('#### Try an issue')
        cols = st.columns(4)
        for col, name in zip(cols, EXAMPLES):
            col.button(name, on_click=set_example, args=(name,), use_container_width=True)
        st.text_input('Issue title', key='issue_title')
        st.text_area('Description', key='issue_body', height=90)
        text = f"{st.session_state['issue_title']} {st.session_state['issue_body']}".strip()
        clicked = st.button('Classify issue', type='primary')
    if clicked:
        try:
            st.session_state['prediction'] = (text, predict_issue(model, vocab, text))
        except ValueError as error:
            st.session_state.pop('prediction', None)
            st.warning(str(error))
    saved = st.session_state.get('prediction')
    if saved and saved[0] == text:
        _, nb, _ = load_ir_and_nb_models()
        show_prediction(saved[1], nb, text)
    elif saved:
        st.info('Input changed. Click Classify issue to update the output.')
    if report:
        show_evaluation(report)
    st.markdown('#### How this connects to the practicals')
    st.write('Words → learned vectors → 3-word convolution → ReLU → global max pooling → dropout → feedforward output → four probabilities.')
    st.caption('P3: feedforward prediction, adapted to text. P4: Adam with mini-batches, not a six-optimizer comparison. P5: measured dropout comparison. P6: 1D text convolution and pooling, not the specified 4×4 image experiment. P7: transfer learning is not implemented.')
