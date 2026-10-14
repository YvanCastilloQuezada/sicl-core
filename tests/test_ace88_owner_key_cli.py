import base64
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from sicl.ace88_owner_key_cli import enroll, sign
from sicl.human_authority_crypto import verify_approval
from sicl.repository import SQLiteRepository


def test_offline_enroll_and_explicit_sign(tmp_path):
    db = tmp_path / 'test.sqlite'
    repo = SQLiteRepository(db)
    repo.conn.execute("INSERT INTO projects(project_id,name,stage,version,temporal_scope) VALUES ('P','Test','test',1,'proyecto')")
    repo.conn.commit()
    repo.close()
    key = tmp_path / 'private' / 'owner.pem'
    with patch('builtins.input', return_value='REGISTRAR'), patch('getpass.getpass', side_effect=['a'*20,'a'*20]):
        enroll(db=str(db), project='P', actor='owner', key_id='k1', key_file=str(key))
    assert key.stat().st_mode & 0o077 == 0
    request = tmp_path / 'request.json'
    request.write_text(json.dumps(dict(projectId='P',proposalId='prop',fingerprint='a'*64,actorId='owner',reviewId='rev',keyId='k1')))
    output = tmp_path / 'approval.json'
    with patch('builtins.input', return_value='APROBAR D2'), patch('getpass.getpass', return_value='a'*20):
        sign(request_file=str(request),key_file=str(key),output_file=str(output))
    signed = json.loads(output.read_text())
    repo = SQLiteRepository(db)
    trusted = repo.trusted_authority_key('P','k1')
    assert verify_approval(payload=signed['approval_payload'],signature_b64=signed['approval_signature_b64'],
        public_key_b64=trusted['public_key_b64'],project_id='P',proposal_id='prop',fingerprint='a'*64,review_id='rev',key_id='k1')
    repo.close()


def test_enroll_requires_human_confirmation(tmp_path):
    with patch('builtins.input', return_value='NO'):
        with pytest.raises(ValueError,match='HUMAN_CONFIRMATION_REQUIRED'):
            enroll(db=str(tmp_path/'x.db'),project='P',actor='owner',key_id='k',key_file=str(tmp_path/'k.pem'))
    assert not (tmp_path/'k.pem').exists()
