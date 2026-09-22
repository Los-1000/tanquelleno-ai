# Lunetra IA — atajos reproducibles de modelado y evaluación
# Uso: make ayuda

PYTHON ?= python3

.PHONY: ayuda instalar macro entrenar inferir auditoria pruebas todo limpiar

ayuda:
	@echo "Lunetra IA — comandos disponibles"
	@echo ""
	@echo "  make instalar   Instala las dependencias de requirements.txt"
	@echo "  make macro      Descarga WTI, Brent y tipo de cambio (requiere internet)"
	@echo "  make entrenar   Entrena el componente analítico A2 (tendencia mensual)"
	@echo "  make inferir    Ejecuta el pipeline end-to-end para Lima"
	@echo "  make auditoria  Mide el KR2 (0% de alucinaciones) sobre 60 casos"
	@echo "  make pruebas    Corre la suite del contrato de modelado (17 pruebas)"
	@echo "  make todo       Cadena completa: entrenar + auditoria + pruebas"
	@echo "  make limpiar    Elimina artefactos generados (modelos y reportes)"

instalar:
	$(PYTHON) -m pip install -r requirements.txt

macro:
	$(PYTHON) scripts/obtener_macro.py

entrenar:
	$(PYTHON) modelado/entrenamiento_a2.py

inferir:
	$(PYTHON) pipeline_inferencia.py --departamento LIMA --nivel-tanque bajo

auditoria:
	$(PYTHON) pipeline_inferencia.py --auditoria-kr2 60

pruebas:
	$(PYTHON) -m pytest tests/ -v

todo: entrenar auditoria pruebas

limpiar:
	rm -f modelos/*.joblib reportes/*.json datos/dataset_maestro_mensual.parquet
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
