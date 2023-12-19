import logging
import os


import click

from vcron import __version__
from vcron.app import VCron


logger = logging.getLogger(__name__)


def setup_log(enabled, level, loglocation):
    if enabled:
        logging.basicConfig(
            filename=os.path.expanduser(loglocation),
            filemode="a",
            format=(
                "%(asctime)s %(levelname)5s (%(module)sL%(lineno)d)"
                " %(message)s"
            ),
            level=level,
        )
    else:
        logging.disable(logging.CRITICAL)
    logger.info("------ vcron ------")


LOG_LEVEL = {
    0: logging.CRITICAL,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}


def run_app(verbose, log_to):
    log_level = LOG_LEVEL[verbose]
    setup_log(log_to is not None, log_level, log_to)

    app = VCron(watch_css=True)
    app.run()


def print_version(ctx, _, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.command(help="Interactive TUI Crontab Editor")
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=2,
    help="Add log verbose level, using -v, -vv, -vvv for printing more logs.",
)
@click.option(
    "-l",
    "--log-to",
    type=click.Path(),
    default=None,
    help="Printing logs to a file, for debugging, default is no logs.",
)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
)
def main(verbose, log_to):
    run_app(verbose, log_to)


if __name__ == "__main__":
    main()
