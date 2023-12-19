from vcron.app import VCron


async def test_app_startup():
    app = VCron()
    async with app.run_test() as pilot:
        assert True
