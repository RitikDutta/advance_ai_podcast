from sequencer import Sequencer


sequencer = Sequencer(10, True)
sequencer.create_sequence('female')

sequencer2 = Sequencer(10, False)
sequencer2.create_sequence('male')