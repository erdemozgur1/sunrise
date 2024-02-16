# Use the base image for Dataflow Python 3 template launcher
FROM gcr.io/dataflow-templates-base/python3-template-launcher-base

# Set up the working directory
WORKDIR /template
ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="/template/requirements.txt"
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/main.py"

# Create folder for Teradata ODBC driver
RUN mkdir -p /opt/teradata_odbc_driver

# Copy and extract Teradata ODBC driver
COPY tdodbc2000__linux_x8664.20.00.00.04-1.tar.gz /opt/teradata_odbc_driver/
RUN tar -xzvf /opt/teradata_odbc_driver/tdodbc2000__linux_x8664.20.00.00.04-1.tar.gz -C /opt/teradata_odbc_driver/ \
    && rm /opt/teradata_odbc_driver/tdodbc2000__linux_x8664.20.00.00.04-1.tar.gz

# Copy project files
COPY function.py main.py requirements.txt /template/

# Install dependencies
RUN apt-get update && \
    apt-get install -y libffi-dev git && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r $FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE && \
    pip download --no-cache-dir --dest /tmp/dataflow-requirements-cache -r $FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE && \
    rm -rf /tmp/dataflow-requirements-cache

# Set environment variables for ODBC driver
ENV ODBCINI=/opt/teradata_odbc_driver/odbc.ini
ENV ODBCSYSINI=/opt/teradata_odbc_driver

# Set environment variable to skip unnecessary dependency installation during runtime
ENV PIP_NO_DEPS=True

# Run your script when the container launches
ENTRYPOINT ["python", "main.py"]
