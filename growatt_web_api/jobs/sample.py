from RoundBox.core.cliparser.jobs import BaseJob, HourlyJob


class Job(HourlyJob):
    help = "My sample job."

    def execute(self):
        # executing empty sample job
        pass
