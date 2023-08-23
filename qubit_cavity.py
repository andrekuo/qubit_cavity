import numpy as np
from qiskit_metal import Dict
from qiskit_metal.qlibrary.core import QRoute, QRoutePoint
from qiskit_metal.qlibrary.core import QComponent
from cavity_feedline import CavityFeedline
from qiskit_metal.qlibrary.qubits.transmon_cross import TransmonCross

class QubitCavity(QComponent):
    
    default_options = dict(
        cavity_options = dict(
            coupler_options = dict(
                orientation = '180',
                coupling_length = '200um'
            ),
            cpw_options = dict(
                total_length = '4000um',
                    left_options = dict(
                        lead = Dict(
                        start_straight = '50um',
                    ),
                ),
            )
        ),
        qubit_options = dict(
            connection_pads=dict(
                c = dict(connector_location = '90', 
                        connector_type = '0',
                    ),
            ),
            orientation = '180',
            pos_y = '1500um'
        )
    )
    
    component_metadata = dict(short_name='qubitcavity')
    """Component metadata"""

    # default_options = dict(meander=dict(spacing='200um', asymmetry='0um'),
    #                        snap='true',
    #                        prevent_short_edges='true')
    """Default options"""

    def copier(self, d, u):
        for k, v in u.items():
            if not isinstance(v, str) and not isinstance(v, float):
                d[k] = self.copier(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    def make(self):
        p = self.p
        self.make_qubit()
        self.make_cavity()
        self.make_pins()
        
    def make_qubit(self):
        p = self.p

        qubit_opts = dict()
        self.copier(qubit_opts, p.qubit_options)
        self.qubit = TransmonCross(self.design, "{}_xmon".format(self.name), options = qubit_opts)
        # print(self.qubit.qgeometry_dict('path'))
        # print(self.qubit.qgeometry_list('poly'))

        # self.add_qgeometry('path', self.qubit.qgeometry_dict('path'))
        # self.add_qgeometry('poly', self.qubit.qgeometry_dict('poly'))

    def make_cavity(self):
        p = self.p

        cavity_opts = dict()
        self.copier(cavity_opts, p.cavity_options)
        cavity_opts['cpw_options'].update({'pin_inputs':dict(
                                            start_pin = dict(
                                                component = '',
                                                pin = ''
                                            ),
                                            end_pin = dict(
                                                component = '',
                                                pin = ''
                                            )
                                            )})
        cavity_opts['cpw_options']['pin_inputs']['start_pin']['component'] = self.qubit.name
        cavity_opts['cpw_options']['pin_inputs']['start_pin']['pin'] = 'c'
        self.cavity = CavityFeedline(self.design, "{}_cavityfeedline".format(self.name), options = cavity_opts)
        # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        # print(self.cavity.qgeometry_dict('path'))
        # self.add_qgeometry('path', self.cavity.qgeometry_dict('path'))
        # self.add_qgeometry('poly', self.cavity.qgeometry_dict('poly'))


    def make_pins(self):
        start_dict = self.cavity.get_pin('prime_start')
        end_dict = self.cavity.get_pin('prime_end')
        self.add_pin('prime_start', start_dict['points'], start_dict['width'])
        self.add_pin('prime_end', end_dict['points'], end_dict['width'])
