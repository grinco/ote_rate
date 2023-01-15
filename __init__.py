from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from .const import (
    CONF_CURRENCY,
    DOMAIN,
    CONF_EXCHANGE_RATE,
    CONF_EXCHANGE_RATE_SENSOR_ID,
    CURRENCY_CZK,
    CURRENCY_EUR,
    CONF_CHARGE,
    DEFAULT_NAME,
)

"""OTE Rate sensor integration."""
PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""

    config = entry.options
    name = config[CONF_NAME]

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][name] = entry.data

    # Forward the setup to the sensor platform.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

class OteRateHub:
    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        currency: str,
        charge: float | None,
        modbus_addr,
        interface,
        serial_port,
        baudrate,
        scan_interval,
        plugin,
        config
    ):
        """Initialize the Modbus hub."""
        _LOGGER.debug(f"solax modbushub creation with interface {interface} baudrate (only for serial): {baudrate}")
        self._hass = hass
        if (interface == "serial"):
            self._client = ModbusSerialClient(method="rtu", port=serial_port, baudrate=baudrate, parity='N', stopbits=1, bytesize=8, timeout=3)
        else:
            self._client = ModbusTcpClient(host=host, port=port, timeout=5)
        self._lock = threading.Lock()
        self._name = name
        self._modbus_addr = modbus_addr
        self._seriesnumber = 'still unknown'
        self.interface = interface
        self.read_serial_port = serial_port
        self._baudrate = int(baudrate)
        self._scan_interval = timedelta(seconds=scan_interval)
        self._unsub_interval_method = None
        self._sensors = []
        self.data = { "_repeatUntil": {}} # _repeatuntil contains button autorepeat expiry times
        self.cyclecount = 0 # temporary - remove later
        self.slowdown = 1 # slow down factor when modbus is not responding: 1 : no slowdown, 10: ignore 9 out of 10 cycles
        self.inputBlocks = {}
        self.holdingBlocks = {}
        self.computedSensors = {}
        self.computedButtons = {}
        self.writeLocals = {} # key to description lookup dict for write_method = WRITE_DATA_LOCAL entities
        self.sleepzero = [] # sensors that will be set to zero in sleepmode
        self.sleepnone = [] # sensors that will be cleared in sleepmode
        self.writequeue = {} # queue requests when inverter is in sleep mode
        _LOGGER.debug(f"{self.name}: ready to call plugin to determine inverter type")
        self.plugin = plugin.plugin_instance #getPlugin(name).plugin_instance
        self.wakeupButton = None
        self._invertertype = self.plugin.determineInverterType(self, config)
        self._lastts = 0  # timestamp of last polling cycle
        self.localsUpdated = False
        self.localsLoaded = False
        _LOGGER.debug("solax modbushub done %s", self.__dict__)