import pytest
from pathlib import Path
from u_utilities.u_remote.src.pusher import Pusher

def test_pusher_exclusion_logic(tmp_path):
    # Setup mock project structure
    root_dir = tmp_path / "project"
    root_dir.mkdir()
    
    (root_dir / "src").mkdir()
    (root_dir / "src" / "main.py").touch()
    
    (root_dir / "old").mkdir()
    (root_dir / "old" / "legacy.py").touch()
    
    (root_dir / ".git").mkdir()
    (root_dir / ".git" / "config").touch()
    
    (root_dir / "__pycache__").mkdir()
    
    pusher = Pusher(remote_host="mock", remote_dir="mock")
    
    # Test cases
    assert not pusher._is_excluded(root_dir / "src" / "main.py", root_dir)
    assert pusher._is_excluded(root_dir / "old" / "legacy.py", root_dir)
    assert pusher._is_excluded(root_dir / "old", root_dir)
    assert pusher._is_excluded(root_dir / ".git" / "config", root_dir)
    assert pusher._is_excluded(root_dir / "__pycache__", root_dir)

def test_pusher_zip_creation(tmp_path):
    root_dir = tmp_path / "project"
    root_dir.mkdir()
    (root_dir / "src").mkdir()
    (root_dir / "src" / "main.py").write_text("print('hello')")
    (root_dir / "old").mkdir()
    (root_dir / "old" / "bad.py").touch()
    
    zip_path = tmp_path / "code.zip"
    pusher = Pusher(remote_host="mock", remote_dir="mock")
    pusher.create_zip(zip_path, root_dir)
    
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zf:
        namelist = zf.namelist()
        assert "src/main.py" in namelist
        assert "old/bad.py" not in namelist
        assert not any(name.startswith("old/") for name in namelist)
