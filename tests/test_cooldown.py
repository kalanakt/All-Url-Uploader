from services.cooldown import CooldownManager


def test_authorized_users_bypass_cooldown():
    cooldown = CooldownManager(timeout_seconds=60)

    assert cooldown.check(1, {1}) == 0
    assert cooldown.check(1, {1}) == 0


def test_unauthorized_users_are_limited():
    cooldown = CooldownManager(timeout_seconds=60)

    assert cooldown.check(10, set()) == 0
    remaining = cooldown.check(10, set())

    assert 0 < remaining <= 60
