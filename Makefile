# Makefile for Sistema de Gestión de Tareas

.PHONY: help install test test-unit test-integration test-acceptance test-coverage clean run

help:
	@echo "Comandos disponibles:"
	@echo "  install          - Instalar dependencias"
	@echo "  run              - Ejecutar la aplicación"
	@echo "  test             - Ejecutar todas las pruebas"
	@echo "  test-unit        - Ejecutar pruebas unitarias"
	@echo "  test-integration - Ejecutar pruebas de integración"
	@echo "  test-acceptance  - Ejecutar pruebas de aceptación"
	@echo "  test-coverage    - Ejecutar pruebas con reporte de cobertura"
	@echo "  clean            - Limpiar archivos temporales"

install:
	pip install -r requirements.txt

run:
	python run.py

test:
	pytest

test-unit:
	pytest tests/unit/ -m unit

test-integration:
	pytest tests/integration/ -m integration

test-acceptance:
	pytest tests/acceptance/ -m acceptance

test-coverage:
	pytest --cov=app --cov-report=html --cov-report=term-missing

clean:
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf app/__pycache__/
	rm -rf app/*/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf tests/*/__pycache__/
	rm -f .coverage
	rm -f coverage.xml
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete