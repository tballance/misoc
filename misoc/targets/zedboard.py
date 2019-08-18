
from migen import *
from migen.build.platforms import zedboard
from misoc.integration.builder import *

# Import from migen-axi and fix-up
from migen_axi.integration.soc_core import SoCCore as AXISoCCore


class SoCCore(AXISoCCore):
    def __init__(self, platform):
        super().__init__(
            platform=platform,
            csr_data_width=32,
            )

        self._memory_groups = []
        self._csr_groups = []

        self.integrated_rom_size = 0
        self.cpu_type = "cortex-a9"

    def add_memory_group(self, group_name, members):
        self._memory_groups.append((group_name, members))

    def add_csr_groups(self, group_name, members):
        self._csr_groups.append((group_name, members))


    def get_memory_regions(self):
        return self._memory_regions

    def get_memory_groups(self):
        return self._memory_groups

    def get_csr_regions(self):
        return self._csr_regions

    def get_csr_groups(self):
        return self._csr_groups

    def get_constants(self):
        return self._constants

from misoc.interconnect.csr import *

class TestModule(Module, AutoCSR):
    def __init__(self):
        self.clock_domains.cd_sys = ClockDomain()

        self.storage = CSRStorage(32, reset=0x12345678)

        self.counter = CSRStatus(32)
        counter = Signal(32)
        self.sync += counter.eq(counter + 1)
        self.comb += self.counter.status.eq(counter)


class BaseSoC(SoCCore):
    def __init__(self):

        platform = zedboard.Platform()
        super().__init__(platform=platform)

        fclk0 = self.ps7.fclk.clk[0]
        self.clock_domains.cd_sys = ClockDomain()
        self.specials += Instance("BUFG", i_I=fclk0, o_O=self.cd_sys.clk)

        self.submodules.test = TestModule()
        self.csr_devices.append("test")
        
        self.comb += self.test.cd_sys.clk.eq(self.cd_sys.clk)


def main():

    soc = BaseSoC()
    builder = Builder(soc)
    builder.software_packages = []
    builder.build()


if __name__ == "__main__":
    main()
