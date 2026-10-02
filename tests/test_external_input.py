"""Regression tests for the external-input runtime port (MIDI parsing)."""

from noisemaker_cpu.external_input import MidiState


def test_channel_pressure_two_byte_message_is_routed():
    """[0xD0, pressure] is a valid two-byte channel-pressure message: the JS
    oracle reads the absent velocity byte as `undefined` and exempts 0xD0 from
    the velocity check (external-input.js handleMessage), so parsing must not
    raise and the pressure must land on the channel."""
    state = MidiState()
    assert state.handle_message([0xD0, 64]) == 0
    assert state.channels[1].pressure == 64


def test_program_change_needs_a_velocity_byte_like_the_oracle():
    """The oracle's velocity check exempts only 0xD0, so a two-byte program
    change is unhandled there (velocity undefined) and a three-byte one routes
    (verified against external-input.js at b0e6c4130ac2: `[0xC0,5]` -> -1,
    `[0xC0,5,0]` -> 0 program 5)."""
    state = MidiState()
    assert state.handle_message([0xC0, 5]) == -1
    assert state.handle_message([0xC0, 5, 0]) == 0
    assert state.channels[1].program == 5


def test_one_byte_channel_message_is_unrouted():
    """A bare status byte (key undefined in the oracle) is unhandled, not an
    IndexError."""
    state = MidiState()
    assert state.handle_message([0xC0]) == -1
    assert state.handle_message([0xD0]) == -1
