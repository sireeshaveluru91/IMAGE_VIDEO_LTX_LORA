PYTHON ?= python
export PYTHONPATH := src
PACKAGE = image_video_ltx_lora
DOCKER_IMG ?= ltx-image2video:dev
CONFIG ?= configs/default.yaml
OUTPUT ?= outputs

.PHONY: setup fmt lint test run dry-run docker-build docker-push clean

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .[dev]
	pre-commit install || true

fmt:
	ruff format src tests

lint:
	ruff check src tests

test:
	pytest -q

run:
	$(PYTHON) -m src.main run $(CONFIG) --output-dir $(OUTPUT)

dry-run:
	$(PYTHON) -m src.main run $(CONFIG) --output-dir $(OUTPUT) --dry-run

docker-build:
	docker build --platform linux/amd64 --tag $(DOCKER_IMG) -f docker/Dockerfile .

docker-push:
	docker push $(DOCKER_IMG)

clean:
	rm -rf dist build *.egg-info __pycache__
