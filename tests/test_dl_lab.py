"""Regression tests for honest inference, split isolation, and live UI behavior."""
import json
from pathlib import Path
from collections import defaultdict

import pyarrow.parquet as pq
import pytest
import torch
from streamlit.testing.v1 import AppTest

from src.common.config import CURATED_DATA_DIR, DL_MAX_LEN
from src.ir.index import tokenize
from src.ir.split import assign_clean_splits
from src.ml.dataset import IssueVocabulary
from src.ml.inference import predict_issue
from src.ml.model import create_issue_cnn
from src.ml.train import fingerprint, score_predictions


def test_deduplication_precedes_split_and_is_repeatable():
    rows = [dict(event_id=str(i), repo_name='repo', issue_number=i, title=f'crash module_{i}',
                 body='', label='bug') for i in range(20)]
    rows += [dict(rows[0], event_id='reopened'), dict(rows[1], event_id='copy', issue_number=99)]
    result = assign_clean_splits(rows)
    assert len(result) == 20
    assert result == assign_clean_splits(list(reversed(rows)))
    assert {r['split'] for r in result} == {'train','val','test'}


def test_real_split_has_no_issue_or_processed_input_overlap():
    rows = pq.read_table(CURATED_DATA_DIR/'splits.parquet').to_pylist()
    for key in (lambda r:(r['repo_name'],r['issue_number']),
                lambda r:tuple(tokenize(f"{r['title']} {r['body']}")[:DL_MAX_LEN])):
        groups = defaultdict(set)
        for row in rows:
            groups[key(row)].add(row['split'])
        assert all(len(splits) == 1 for splits in groups.values())


def test_inference_calls_forward_and_rejects_uninformative_input():
    vocab = IssueVocabulary(min_freq=1)
    vocab.build_from_texts(['crash parser memory'])
    model = create_issue_cnn(len(vocab))
    calls = []
    handle = model.register_forward_hook(lambda *args: calls.append(True))
    a = predict_issue(model, vocab, 'crash parser')
    b = predict_issue(model, vocab, 'crash parser')
    handle.remove()
    assert len(calls) == 2
    assert a['probabilities'] == b['probabilities']
    assert sum(a['probabilities'].values()) == pytest.approx(1)
    assert a['trace']['fc'] == [1,4]
    assert a['trace']['dropout'] == [1,64]
    assert predict_issue(model, vocab, 'crash ' * 51)['truncated']
    for text in ('', '!!!', 'zzzzunknown'):
        with pytest.raises(ValueError):
            predict_issue(model, vocab, text)


def test_saved_report_matches_artifacts_and_confusion_counts():
    report = json.loads((CURATED_DATA_DIR/'dl_report.json').read_text())
    for name, digest in report['artifacts'].items():
        assert fingerprint(CURATED_DATA_DIR/name) == digest
    assert sum(map(sum,report['cnn']['confusion_matrix'])) == report['split_counts']['test']
    scores = score_predictions([0,1,2,3],[0,1,2,3])
    assert scores['accuracy'] == scores['macro_f1'] == 1


def test_app_navigation_presets_inference_and_blank_input():
    app = AppTest.from_file(str(Path('src/app/main.py').resolve()), default_timeout=30).run()
    assert not app.exception
    for section in ('Issue search','Archive download','About me','Search categories'):
        app.radio[0].set_value(section).run()
        assert not app.exception
    app.button[2].click().run()  # Documentation preset
    assert app.text_input[0].value == 'Update installation instructions in README'
    app.button[-1].click().run()
    assert not app.exception
    assert any('Suggested label:' in title.value for title in app.subheader)
    app.text_input[0].set_value('').run()
    app.text_area[0].set_value('').run()
    app.button[-1].click().run()
    assert not app.exception
    assert any('meaningful word' in warning.value for warning in app.warning)
