lint:
  poetry run isort . --check
  poetry run black --check .
  poetry run pyright .

