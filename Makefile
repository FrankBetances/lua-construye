.PHONY: ejemplo-s1 sets-todos

# Recorre el Set 1 con los siete agentes y deja los artefactos en sets/S1-camino/.
ejemplo-s1:
	python3 -m agents.pipeline

# Probeta, kit y sets 2 a 6. No regenera sets/S1-camino.
sets-todos:
	python3 -m agents.pipeline_todos
