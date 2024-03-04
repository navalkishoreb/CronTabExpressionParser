import argparse

from parser.models import CronJob

parser = argparse.ArgumentParser(prog="python -m parser")
parser.add_argument("input_string", type=str, help="cron tab expression")
args = parser.parse_args()
cron_expression = args.input_string
cron_job = CronJob(expression=cron_expression)
print(cron_job)
