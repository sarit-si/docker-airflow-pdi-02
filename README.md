# Description

Step by step approach to easily dockerize Airflow and Pentaho Data Integration **IN SAME CONTAINER**.
Below is the high level architecture of the image setup:
    - Airflow is the orchestrator which runs Bash command to trigger PDI task within the same container
    - PDI (with no Carte) within the same container performs the actual task (transformation/job) assigned by Airflow


# Pre-requisites
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

# Versions
- Airflow 2.0
- PDI 9.1

 # Setup
Change directory to the project folder before performing below steps.

### Environment variables, files & folders for container
- Create a .env file and add the user and group Ids.
This is required for the container to have same access privileges as that of the host user during docker compose.

        echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env

- If needed, append the below optional variables to the above .env file.

        echo -e "<variable name>=<value>" >> .env
    - HOST_ENV --> run container as localhost/dev/qa/prod. This will copy corresponding kettle.properties into the container. Also enables PDI transformations to pick environment specific DB JNDI connections during execution. Can be used by Airflow to connect to corresponding resources.
    - AIRFLOW_ADMIN_USER --> Create Web UI user. Default: airflow
    - AIRFLOW_ADMIN_PASSWORD --> Default: airflow
    - AIRFLOW_ADMIN_EMAIL --> Required if new user to be created
    - PENTAHO_DI_JAVA_OPTIONS --> Allocate JVM memory to PDI container, based on host machine RAM. Increase if container crashes due to GC Out of memory. Ex: for Min. 1G and Max 4G, set this to "-Xms1g -Xmx4g"
    - AIRFLOW_HOST_PORT --> Default: 8080

 - Create below folders for the container volumes to bind with host.

        mkdir -p ./setup-airflow-pdi/logs/airflow ./setup-airflow-pdi/logs/pdi ./setup-airflow-pdi/plugins


- Source Code
Since the DAGs/PDI source code files might undergo frequent updates, they are not copied into the container during image build, instead mounted via docker compose. Any update to these source code files on host will automatically get visible inside the container.

  - Airflow:
    - Default folder for DAGs on host is ./source-code/dags
    - Replace the above default folder in the docker compose file, with the desired folder location on host.
    - Place all the DAG files in the above host dags folder.

  - Pentaho:
    - Default folder for ktr/kjb files on host is ./source-code/ktrs
    - Replace the above default folder in the docker compose file, with the desired folder location on host.
    - Place all the PDI files in the above host ktrs folder.

### Build & Deploy
Below command will build (if first time) and start all the services.

        docker-compose up
To run as daemon, add -d option.

# Web UI
- If not localhost, replace with server endpoint Url
- If not below default ports, replace with the ones used during AIRFLOW_HOST_PORT setup.

Airflow Webserver

        localhost:8080/home

# How to trigger tasks from a DAG

Since there is no Carte server, the tasks will be executed by running PDI via kitchen.sh/pan.sh directly. Tasks are run in the same container as that of Airflow.

Job trigger:

        job = BashOperator(
                task_id='Trigger_Job',
                bash_command='/opt/airflow/data-integration/kitchen.sh -file:/opt/airflow/ktrs/helloworld/helloworld-job.kjb'
        )

Transformation trigger:

        trans = BashOperator(
                task_id='Trigger_Transformation',
                bash_command='/opt/airflow/data-integration/pan.sh -file:/opt/airflow/ktrs/helloworld/helloworld-trans.ktr'
        )

- Parameters can be passed by adding /param:, ex: /param:param1=value1 /param:param2=value2

# Best practices
- ```jdbc.properties``` file, which contains database access credentials, has been included in this repo for reference purpose only. In actual development, this should be avoided and needs to be added to gitignore instead. After first code pull to a server, update it with all JNDI details before docker compose.

- ```.env``` file also may contain sensitive information, like environment dependent access keys. This also should be added to .gitignore file. Instead create this file with necessary parameters during image build.

- ```HOST_ENV``` setting this parameter gives us a flexibility to choose appropriate ```kettle.properties``` file. For example, QA and PROD mailing server SMTP details may differ. This can be included in separate kettle properties file, to be selected dynamically based on the host environment. Not only this, if one uses the ```jdbc.properties``` file, we can enable PDI container dynamically select the correct JNDI from ```jdbc.properties``` file. For ex: if one needs to test a transformation in QA environemnt using Postgres JNDI connection encoded as ```db-${HOST_ENV}```, running PDI with ```HOST_ENV=qa```, will render ```db-qa``` database JNDI, thus using QA data for testing.

- ```PENTAHO_DI_JAVA_OPTIONS``` Having this option lets the user tweak the amount of memory PDI gets inside the container, to run a task. Depending on the host machine memory and average task complexity, this can be modified to avoid container crash due to "GC Out of Memory" errors. If host machine has ample RAM and PDI container is crashing due to the default memory limits, we can increase it by setting ```PENTAHO_DI_JAVA_OPTIONS=-Xms1g -Xmx4g``` 1GB and 4GB being the lower and upper limits respectively.

