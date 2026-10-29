.PHONY: ejemplo-s1 sets-todos check lua-v5

FIRMWARE ?= ../lua-firmware

# Recorre el Set 1 con los siete agentes y deja los artefactos en sets/S1-camino/.
ejemplo-s1:
	python3 -m agents.pipeline

# Probeta, kit y sets 2 a 6. No regenera sets/S1-camino.
sets-todos:
	python3 -m agents.pipeline_todos

# Trae de lua-firmware la interfaz de Lúa V5 y su patín (lua-v5/).
lua-v5:
	@echo "la interfaz del cubo se escribe a mano en lua-v5/; make check la compara"

# Las medidas con Lúa: que la copia de lua-v5/ sea la de lua-firmware y que
# Lúa V5 corra por el Set 1 y entre en el zócalo. Sin el vecino, se saltan.
check:
	python3 -m agents.lua_v5 --check $(FIRMWARE)
	python3 -m agents.check_lua_camino --firmware $(FIRMWARE)
