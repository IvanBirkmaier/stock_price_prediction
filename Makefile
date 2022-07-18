
.PHONY: data
data:
	python backend\services\featureEningering\featureEningering.py

.PHONY: runlstm
runlstm:
	python backend\services\neuronalNetworks\pytorchlstm.py

.PHONY: gitcommit
gitcommit:
	git status
	git add .
	git commit -m "auto commit from makefile"

.PHONY: initdb
initdb:
	python backend\services\database\initDatabase.py

.PHONY: bootbackend
bootbackend:
	uvicorn backend.controller.apiController:app --reload

.PHONY: visufeature
visufeature:
	python backend\services\visualization\visuFeatureEning.py

.PHONY: visunn
visunn:
	python backend\services\visualization\visuNN.py

.PHONY: db
db:
	mysql -u root 





