# To illustrate how we can trigger a job/transformation

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy import DummyOperator

args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "wait_for_downstream": False,
    "catchup": False,
}


with DAG(
    dag_id="hello-world",
    default_args=args,
    schedule_interval=None,
    catchup=False,
    description=f"Hello World!!!",
) as dag:

    t1 = DummyOperator(
        task_id='Start',
    )

    t2 = BashOperator(
        task_id='Trigger_Job',
        bash_command='/opt/data-integration/kitchen.sh -file:/opt/airflow/ktrs/helloworld/helloworld-job.kjb'
    )

    t3 = BashOperator(
        task_id='Trigger_Transformation',
        bash_command='/opt/data-integration/pan.sh -file:/opt/airflow/ktrs/helloworld/helloworld-trans.ktr'
    )

    t4 = DummyOperator(
        task_id='Stop',
    )

    t1 >> [t2, t3] >> t4