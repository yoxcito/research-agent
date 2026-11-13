clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +

run:
	uv run main.py

sync:
	uv sync