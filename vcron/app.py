import logging
from croniter import croniter
from textual import on
from datetime import datetime
from textual.reactive import reactive
from croniter import CroniterBadCronError
from textual.app import App, ComposeResult
from textual.widgets import Input

from textual.containers import Center, Container, Horizontal, VerticalScroll
from textual.widgets import DirectoryTree, Footer, Header, Static
from cron_descriptor import (
    FormatException,
    get_description,
    MissingFieldException,
    WrongArgumentException,
)

from textual.validation import Function, Number, ValidationResult, Validator


logger = logging.getLogger(__name__)

FUTURE_PREDICT = 300


class InvalidCrontab(Exception):
    """Invalid Crontab"""


def input_to_description(value):
    parts = value.split(" ")
    if len(parts) == 6:
        seconds_to_last = [parts[-1], *parts[:-1]]
        return " ".join(seconds_to_last)
    if len(parts) < 6:
        return value
    raise InvalidCrontab(
        "Expression has too many parts ({}).  Expression must not have"
        " more than 6 parts.".format(len(parts))
    )


class CrontabValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        try:
            value = input_to_description(value)
            logger.debug("validate: %s", value)
            get_description(value)
        except (
            FormatException,
            MissingFieldException,
            WrongArgumentException,
            InvalidCrontab,
        ) as e:
            return self.failure(str(e))
        else:
            return self.success()


class VCron(App):
    CSS_PATH = "vcron.tcss"

    crontab_input = reactive("")

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        yield Header(show_clock=True, name="Vcron")
        with Center():
            yield Static(id="crontab-explain")
        with Center():
            yield Container(
                Input(
                    placeholder="Input a crontab...",
                    id="crontab-input",
                    valid_empty=False,
                    validators=[CrontabValidator()],
                ),
                id="crontab-input-container",
            )
        with Center():
            yield Horizontal(
                Static("minute"),
                Static("hour"),
                Static("day"),
                Static("month"),
                Static("day_of_week"),
                Static("(seconds?)"),
                id="part-hint-container",
            )
        with Center():
            v = VerticalScroll(
                Static(id="crontab-future"),
                id="crontab-future-container",
            )
            v.border_title = f"Next {FUTURE_PREDICT} runs on:"
            yield v
        yield Footer()

    @on(Input.Changed)
    def handle_input_changed(self, event):
        input_text = event.value
        logger.info(
            "input chagned: %s, %r", input_text, event.validation_result
        )
        self.crontab_input = input_text

        explain_static = self.query_one("Static#crontab-explain")
        future_static = self.query_one("Static#crontab-future")

        if event.validation_result.is_valid:
            description_text = input_to_description(input_text)
            explain_text = get_description(description_text)
            explain_static.update(explain_text)
            explain_static.remove_class("error")

            base = datetime.now().replace(microsecond=0)
            try:
                it = croniter(input_text, base)
                text = [f"Next {FUTURE_PREDICT} runs on: \n"]

                last_run = None
                for _ in range(FUTURE_PREDICT):
                    run_time = it.get_next(datetime)
                    if last_run:
                        duration = run_time - last_run
                        duration_text = f"{str(duration)} after last run."
                    else:
                        duration = run_time - base
                        duration_text = f"in {str(duration)} from now."
                    last_run = run_time
                    text.append(
                        f'{run_time.strftime("%Y-%m-%d %H:%M:%S")} [grey42]{duration_text}[/grey42]'
                    )
                future_static.update("\n".join(text))
            except CroniterBadCronError as e:
                self.display_error(str(e))
        else:
            self.display_error(
                "".join(event.validation_result.failure_descriptions)
            )

    def display_error(self, error_msg):
        explain_static = self.query_one("Static#crontab-explain")
        future_static = self.query_one("Static#crontab-future")
        explain_static.update(error_msg)
        explain_static.add_class("error")
        future_static.update("")
