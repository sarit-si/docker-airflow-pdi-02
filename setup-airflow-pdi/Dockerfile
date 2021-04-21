# Get Base image
FROM openjdk:8-jre AS pdi-builder

LABEL maintainer="saritkumarsi@gmail.com" \
      version="1.0" \
      description="Docker file builds Pentaho Data Integration image"

# Set required environment vars for PDI
ENV PDI_RELEASE=9.1 \
    PDI_VERSION=9.1.0.0-324 \
    PENTAHO_JAVA_HOME=/usr/local/openjdk-8 \
    PENTAHO_HOME=/home/pentaho

# Create home directory
RUN mkdir -p ${PENTAHO_HOME}

# Download PDI
RUN /usr/bin/wget \
    --progress=dot:giga \
    https://sourceforge.net/projects/pentaho/files/Pentaho%20${PDI_RELEASE}/client-tools/pdi-ce-${PDI_VERSION}.zip \
    -P ${PENTAHO_HOME}

# Unzip PDI
RUN /usr/bin/unzip -q ${PENTAHO_HOME}/pdi-ce-${PDI_VERSION}.zip -d /opt/ && \
    rm ${PENTAHO_HOME}/pdi-ce-${PDI_VERSION}.zip

# Install App dependent connectors
# MySQL JDBC Connector
RUN /usr/bin/wget \
    --progress=dot:giga \
    https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.49.zip \
    -P ${PENTAHO_HOME}

RUN /usr/bin/unzip -q ${PENTAHO_HOME}/mysql-connector-java-5.1.49.zip -d ${PENTAHO_HOME} && \
    cp ${PENTAHO_HOME}/mysql-connector-java-5.1.49/mysql-connector-java-5.1.49-bin.jar /opt/data-integration/lib && \
    rm -R ${PENTAHO_HOME}/mysql-connector*


# Get Airflow base image
FROM apache/airflow:2.0.1

LABEL maintainer="saritkumarsi@gmail.com" \
      version="1.0" \
      description="Docker file builds Airflow image"

USER root

# Set environment variables for PDI to use
ENV PENTAHO_JAVA_HOME=/usr/local/openjdk-8
ENV KETTLE_HOME=/opt/data-integration/
ENV PATH=${KETTLE_HOME}:${PATH}

# Create kettle.properties file & make airflow user owner of KETTLE_HOME
RUN mkdir -p ${KETTLE_HOME}/.kettle \
    && chown -R airflow ${KETTLE_HOME} \
# had to add below chmod since pentaho creates PENTAHO_METASTORE_FOLDER in /home/airflow during task initialization.
# Setting the above environment variable does not change the default folder location as cited in https://jira.pentaho.com/browse/PDI-18465 . Without this chmod, PDI was throwing error for not being able to create .pentaho/metastore directory in /home/airflow
    && chmod -R 771 /home/airflow

# Copy only the required pdi built binaries from pdi-builder image above
COPY --from=pdi-builder /opt/data-integration ${KETTLE_HOME}
# COPY --from=pdi-builder /usr/lib/jvm/java-8-openjdk-amd64/ ${PENTAHO_JAVA_HOME}
COPY --from=pdi-builder /usr/local/openjdk-8 /usr/local/openjdk-8

# Change user
USER airflow

# If required, install necessary python packages for Airflow
RUN pip install --upgrade pip && \
    pip install 'apache-airflow[postgres]'