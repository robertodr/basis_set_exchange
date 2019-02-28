'''
Converts basis set data to a specified output format
'''

from .. import sort
from .bsejson import write_json
from .nwchem import write_nwchem
from .g94 import write_g94
from .gamess_us import write_gamess_us
from .psi4 import write_psi4
from .turbomole import write_turbomole

_converter_map = {
    'nwchem': {
        'display': 'NWChem',
        'extension': '.nw',
        'comment': '#',
        'valid': set(['cartesian_gto', 'spherical_gto', 'scalar_ecp']),
        'function': write_nwchem
    },
    'gaussian94': {
        'display': 'Gaussian94',
        'extension': '.gbs',
        'comment': '!',
        'valid': set(['cartesian_gto', 'spherical_gto', 'scalar_ecp']),
        'function': write_g94
    },
    'psi4': {
        'display': 'Psi4',
        'extension': '.gbs',
        'comment': '!',
        'valid': set(['cartesian_gto', 'spherical_gto', 'scalar_ecp']),
        'function': write_psi4
    },
    'gamess_us': {
        'display': 'GAMESS US',
        'extension': '.bas',
        'comment': '!',
        'valid': set(['cartesian_gto', 'spherical_gto', 'scalar_ecp']),
        'function': write_gamess_us
    },
    'turbomole': {
        'display': 'Turbomole',
        'extension': '.tm',
        'comment': '#',
        'valid': set(['cartesian_gto', 'spherical_gto', 'scalar_ecp']),
        'function': write_turbomole
    },
    'json': {
        'display': 'JSON',
        'extension': '.json',
        'comment': None,
        'valid': None,
        'function': write_json
    }
}


def convert_basis(basis_dict, fmt, header=None):
    '''
    Returns the basis set data as a string representing
    the data in the specified output format
    '''

    # Sort the basis dictionary
    basis_dict_sorted = sort.sort_basis_dict(basis_dict)

    # make converters case insensitive
    fmt = fmt.lower()
    if fmt not in _converter_map:
        raise RuntimeError('Unknown basis set format "{}"'.format(fmt))

    converter = _converter_map[fmt]

    # Determine if the converter supports all the types in the basis_dict
    if converter['valid'] is not None:
        ftypes = set(basis_dict['basis_set_function_types'])
        if ftypes > converter['valid']:
            raise RuntimeError('Converter {} does not support all function types: {}'.format(fmt, str(ftypes)))

    # Actually do the conversion
    ret_str = converter['function'](basis_dict_sorted)

    if header is not None and fmt != 'json':
        comment_str = _converter_map[fmt]['comment']
        header_str = comment_str + comment_str.join(header.splitlines(True))
        ret_str = header_str + '\n\n' + ret_str

    # HACK - Psi4 requires the first non-comment line be spherical/cartesian
    #        so we have to add that before the header
    if fmt == 'psi4':
        types = basis_dict['basis_set_function_types']
        harm_type = 'spherical' if 'spherical_gto' in types else 'cartesian'
        ret_str = harm_type + '\n\n' + ret_str

    return ret_str


def get_formats():
    '''
    Returns the available formats mapped to display name.

    This is returned as an ordered dictionary, with the most common
    at the top, followed by the rest in alphabetical order
    '''

    return {k: v['display'] for k, v in _converter_map.items()}


def get_format_extension(fmt):
    '''
    Returns the recommended extension for a given format
    '''

    if fmt is None:
        return 'dict'

    fmt = fmt.lower()
    if fmt not in _converter_map:
        raise RuntimeError('Unknown basis set format "{}"'.format(fmt))

    return _converter_map[fmt]['extension']


def get_valid_formats(function_types):
    '''Return a list of valid formats given a list of function types'''

    ftypes = [x.lower() for x in function_types]
    ftypes = set(function_types)
    ret = []

    for fmt,v in _converter_map.items():
        if v['valid'] is None or ftypes <= v['valid']:
           ret.append(fmt) 
    return ret
