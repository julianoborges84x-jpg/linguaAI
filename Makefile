test-backend:
	python -m pytest -q

test-frontend:
	npm --prefix frontend run test

test-e2e:
	npm --prefix frontend run test:e2e

verify:
	python -m pytest -q
	npm --prefix frontend run verify
