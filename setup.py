from setuptools import setup, find_packages

VERSION = '0.1'
install_requires = [
    'pyramid',
    'pyserial',
    'requests',
    'supervisor',
    'XBee',
]

setup(name='qfi_xbee_sensor',
      version='0.1',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=[],
      entry_points="""\
      [console_scripts]
      logsensors = qfi_xbee_sensor.xbee_sensor:main
      uploadsensors = qfi_xbee_sensor.cosm:main
      webstatus = qfi_xbee_sensor.webui:main
      """
      )
