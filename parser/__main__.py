import argparse

from parser.transformers import transform_cron_expression_to_cron_job

parser = argparse.ArgumentParser(prog="python -m parser")
parser.add_argument("input_string", type=str, help="cron tab expression")
args = parser.parse_args()
cron_expression = args.input_string
cron_job = transform_cron_expression_to_cron_job(expression=cron_expression)
print(cron_job)
