import os
import sys
import subprocess
import traceback
import types

def save_env_yml(results_dir):
    """
    Save the yml to recreate the environment in results_dir.
    """
    cmd = 'conda env export'
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, err = p.communicate()

    if err:
        print('Error when creating env yml file:')
        print(err)

    else:
        fnm = os.path.join(results_dir, 'environment.yml')
        with open(fnm, 'w') as f:
            f.write(output.decode('utf-8'))

        print('Saved environment yml file to: {}'.format(fnm))


def save_parameter_files(results_dir, parser, msg=''):
    """
    Save the command line arguments used, and any py or cfg files.
    Write a custom message to the command used file with the msg parameter.
    """
    cmd_used = ' '.join(sys.argv)
    fnm = os.path.join(results_dir, 'cmd_used.txt')
    with open(fnm, 'w') as f:
        if msg:
            f.write(msg)
        f.write(cmd_used)
    print('Saved command used to: {}'.format(fnm))

    args = parser.view_args()

    if hasattr(args, 'parameters') and args.parameters:
        fnm = args.parameters
        if not os.path.isfile(fnm):
            print('File does not exist: {}'.format(fnm))
        else:
            with open(fnm, 'r') as f:
                contents = ''.join(f.readlines())
            # Remove any path, just keep the filename.
            new_fnm = fnm.split('/')[-1]
            new_fnm = os.path.join(results_dir, new_fnm)
            with open(new_fnm, 'w') as f:
                f.write(contents)
            print('Saved py file to: {}'.format(new_fnm))

    if hasattr(args, 'other_parameters') and args.other_parameters:
        fnm = args.other_parameters[0]
        if not os.path.isfile(fnm):
            print('File does not exist: {}'.format(fnm))
        else:
            with open(fnm, 'r') as f:
                contents = ''.join(f.readlines())
            # Remove any path, just keep the filename.
            new_fnm = fnm.split('/')[-1]
            new_fnm = os.path.join(results_dir, new_fnm)
            with open(new_fnm, 'w') as f:
                f.write(contents)
            print('Saved cfg file to: {}'.format(new_fnm))


def save_provenance(results_dir, *args, **kwargs):
    """
    Store the provenance in results_dir.
    """
    results_dir = os.path.join(results_dir, 'prov')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    try:
        save_env_yml(results_dir)
        save_parameter_files(results_dir, *args, **kwargs)
    except:
        traceback.print_exc()

def save_parameter_as_py(param, file_name, parser):
    """
    Save the Parameter object as a Python file under file_name.
    """
    args = parser.view_args()

    # Dump the imports used in the original Python file,
    # along with all of the attributes in the Parameter object.
    # Any newer values for a parameter will be placed on the bottom
    # of the file, automatically overwriting any old values.
    py_contents = []
    if hasattr(args, 'parameters') and args.parameters:
        fnm = args.parameters
        if not os.path.isfile(fnm):
            print('File does not exist: {}'.format(fnm))
        else:
            with open(fnm, 'r') as f:
                # Add each of the attribute from the Parameter object to the array.
                py_contents = [l for l in f.readlines()]

    for var_name, var_value in vars(param).items():
        if isinstance(var_value, types.ModuleType) or isinstance(var_value, types.FunctionType):
            # We already have an import statement, so this isn't needed.
            # This dumps "<module 'os' from '..'", which invalid anyways.
            continue
        if isinstance(var_value, str):
            line = '{} = \'{}\''
        else:
            line = '{} = {}'
        py_contents.append(line.format(var_name, var_value))
    
    with open(file_name, 'w') as f:
        for l in py_contents:
            if not l.endswith('\n'):
                l += '\n'
            f.write(l)
