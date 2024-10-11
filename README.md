# Welcome to RECORD!
The the REward-COst in Rodent Decision-making (RECORD) is a microcontroller-based system for the design and implementation of behavioural trials with the ability to synchronise with other external neural recording systems. RECORD has a variety of applications, but its main purpose is for behavioural neuroscience implementations.

The system offers modularity and customisability at its core. It includes 3D-printed components, electronics, and software.

## 3D printing
We have personally designed every 3D-printed component of the system, and have provided the [AutoCAD files](https://github.com/rjibanezalcala/RECORD/tree/main/3d-prints/cad) for editing, and the [STL files](https://github.com/rjibanezalcala/RECORD/tree/main/3d-prints/stl) for printing directly. 

## Electronic hardware and firmware
The electronics that drive the RECORD system are cheap but effective. We use an embedded systems approach to allow for customisable trials that can either be automated, or performed manually. The embedded electronics work on a command-servicing routine, which will make the electronics react to commands sent by the user via serial communications.

We chose the [Texas Instruments MSP430-FR2355 microcontroller](https://www.ti.com/tool/MSP-EXP430FR2355) due to its price and versatility. All of RECORD's [microcontroller firmware](https://github.com/rjibanezalcala/RECORD/tree/main/microcontroller) can be found within this repository.

Our custom-designed PCB is a hub for signals to be relayed from the microcontroller to our rodent arenas. We provide all [Gerber files](https://github.com/rjibanezalcala/RECORD/tree/main/pcb) in this repository.

## Software
Within this repository, you will find example scripts and workflows that can be used as templates for designing your own behavioural trials. For example, we have developed software packages designed specifically for our system. These packages allow scripting of customised trials in [Python](https://github.com/rjibanezalcala/RECORD/tree/main/python). We also provide [Ethovision experiments](https://github.com/rjibanezalcala/RECORD/tree/main/ethovision_experiments) and [Bonsai workflows](https://github.com/rjibanezalcala/RECORD/tree/main/bonsai_workflows) containing our custom decision making task.

Specifically for Ethovision, we provided [Batch scripts](https://github.com/rjibanezalcala/RECORD/tree/main/microcontroller/batch_scripts) that allow communication with our microcontroller system within an experiment's trial-control.

Data management is important for high-throughput systems, thus we created [Serendipity](https://github.com/lddavila/UTEP-Brain-Computation-Lab-Remote-Databases-and-Serendipity-App/tree/main/App%20Deployment%20Folder), a databasing and data pre-processing software suite, provided in an outside repository.

Finally, our data analysis software suite, including [behavioural feature extraction tools](https://github.com/atanugiri/Feature-Extraction), [neuroeconomic analysis tools](https://github.com/rjibanezalcala/RECORD/tree/main/data_analysis/neuroeconomic_analysis), [behavioural classification tools](https://github.com/lddavila/UTEP-Brain-Computation-Lab-Remote-Databases-and-Serendipity-App), are all provided within this and outside repositories.

trial_start_tone was created using [Tonegen](https://www.nch.com.au/tonegen/index.html).

## Documentation

The User Manual, Build guides, and other documentation can be found in our [documentation](https://github.com/rjibanezalcala/RECORD/tree/main/documentation) section.
<!--
> Written with [StackEdit](https://stackedit.io/).
-->
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTIzNTUwMDI1Nl19
-->
