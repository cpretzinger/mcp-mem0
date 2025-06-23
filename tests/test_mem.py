import os, sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
import db

os.environ['DATABASE_URL'] = 'memory'

def test_round_trip():
    db.init_db()
    text = "hello world"
    emb = [0.1, 0.2, 0.3]
    mem_id = db.save_memory(text, emb)
    assert mem_id
    all_mem = db.get_all_memories()
    assert text in all_mem
    res = db.search_memories(emb, limit=1)
    assert res[0] == text
