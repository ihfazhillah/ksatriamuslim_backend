from ksatria_muslim.sensors.stream import M3U8Stream


class SensorsCompositionRoot:
    @property
    def streamer(self):
        return M3U8Stream(25)


sensors_composition_root = SensorsCompositionRoot()
