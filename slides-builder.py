import json
import os
import shutil
import string
from datetime import datetime
import math


def init():
    dir_name = str(datetime.now())
    dir_name = dir_name.replace(' ', '-')
    shutil.copytree("beamer-template", dir_name)
    return dir_name


def append_built_scenario(index, latex_directory):
    output_file = open(f"{latex_directory}/scenarios.tex", 'a')
    output_file.write("\\input{scenario_" + str(index) + "}")
    output_file.flush()
    output_file.close()


def prepend_built_scenario(index, latex_directory):
    with open(f"{latex_directory}/scenarios.tex", 'r') as original: data = original.read()
    with open(f"{latex_directory}/scenarios.tex", 'w') as modified: modified.write(
        "\\input{scenario_" + str(index) + "}" + data)


def build_setup_slide(latex_directory, max_node_count):
    dictionary = {
        "max_node_count": f"{max_node_count}"
    }
    write_in_tc_scenario(-1, latex_directory, "setup.template.tex", dictionary)
    prepend_built_scenario(-1, directory)


def write_in_tc_scenario(index, latex_directory, template_file, dictionary):
    with open(f"{latex_directory}/{template_file}", 'r') as file:
        template = string.Template(file.read())
        filled_template = template.substitute(dictionary)
        output_file = open(f"{latex_directory}/scenario_{index}.tex", 'a')
        output_file.write(filled_template)
        output_file.flush()
        output_file.close()


def build_tc_scenario_setup(index, latex_directory, parameters):
    node_count = int(parameters["node_count"])
    input_count = int(node_count / 2) if bool(parameters["single_process_per_node"]) else node_count
    compute_count = math.ceil(float(node_count / 2.0)) if bool(parameters["single_process_per_node"]) else node_count
    ts_comp_size = int(parameters["ts_component"]) * int(parameters["microslice_size"]) / 1024  # in MB
    dictionary = {
        "tc_index": index + 1,
        "nodes_count": node_count,
        "input_count": input_count,
        "compute_count": compute_count,
        "input_buffer": parameters["in_buffer"],
        "compute_buffer": parameters["cn_buffer"],
        "node_theo_bw": parameters["node_theo_bw"],
        "theo_agg_bw": input_count * float(parameters["node_theo_bw"]),
        "node_acc_bw": parameters["node_acc_bw"],
        "achievable_agg_bw": input_count * float(parameters["node_acc_bw"]),
        "delay_ns": parameters["delay_ns"],
        "data_rate": parameters["data_rate"],
        "expected_data_rate": 0,
        "microslice_size": int(parameters["microslice_size"])/1024,  # in KB
        "ms_count": parameters["ts_component"],
        "ts_comp_size": ts_comp_size,
        "timeslice_size": ts_comp_size * input_count,
        "acc_agg_bw": input_count * int(parameters["node_achieved_bw"])
    }
    if dictionary["data_rate"]:
        dictionary["expected_data_rate"] = dictionary["data_rate"]
    else:
        if int(parameters["delay_ns"]) > 0:
            dictionary["expected_data_rate"] = int(parameters["microslice_size"]) * 1000 / int(parameters["delay_ns"])

    write_in_tc_scenario(index, latex_directory, "scenario-setup.template.tex", dictionary)


def build_ts_scenario_buffer_fill_level(index, latex_directory, parameters):
    ts_comp_size = int(parameters["ts_component"]) * int(parameters["microslice_size"]) / 1024  # in MB
    cn_buffer_size = int(parameters["cn_buffer"]) * 1024  # in MB
    buffer_capacity = cn_buffer_size / ts_comp_size
    dictionary = {
        "buffer_ts_component_capacity": buffer_capacity,
        "buffer_size": cn_buffer_size,
        "flesnet_compute_all_buffer_fill_level": f"{parameters['flesnet_dir']}/plots/compute.all.buffer_fill_level.pdf",
        "dfs_compute_all_buffer_fill_level": f"{parameters['dfs_dir']}/plots/compute.all.buffer_fill_level.pdf",
        "flesnet_compute_all_buffer_fill_level_statistics": f"{parameters['flesnet_dir']}/plots/compute.all"
                                                            f".buffer_fill_level_statistics.pdf",
        "dfs_compute_all_buffer_fill_level_statistics": f"{parameters['dfs_dir']}/plots/compute.all"
                                                        f".buffer_fill_level_statistics.pdf"
    }
    write_in_tc_scenario(index, latex_directory, "scenario-buffer-fill-level.template.tex", dictionary)


def build_ts_scenario_input_buffer_usage(index, latex_directory, parameters):
    dictionary = {
        "flesnet_input_buffer_usage": f"{parameters['flesnet_dir']}/plots/input.all.buffer_fill_level.pdf",
        "dfs_input_buffer_usage": f"{parameters['dfs_dir']}/plots/input.all.buffer_fill_level.pdf"
    }
    write_in_tc_scenario(index, latex_directory, "scenario-input-buffer-usage.template.tex", dictionary)


def build_ts_scenario_bandwidth(index, latex_directory, parameters):
    dictionary = {
        "bw_comp_plot": f"{parameters['bw_comp_plot']}"
    }
    write_in_tc_scenario(index, latex_directory, "scenario-bandwidth.template.tex", dictionary)


def build_ts_scenario_ts_completion_duration(index, latex_directory, parameters):
    dictionary = {
        "ts_completion_duration_plot": f"{parameters['ts_completion_duration_comp_plot']}"
    }
    write_in_tc_scenario(index, latex_directory, "scenario-ts-complation-duration.template.tex", dictionary)


def build_ts_scenario_input_buffer_fill_level(index, latex_directory, parameters):
    dictionary = {
        "input_buffer_sent_comp_plot": f"{parameters['input_buffer_sent_comp_plot']}",
        "input_buffer_added_comp_plot": f"{parameters['input_buffer_added_comp_plot']}"
    }
    write_in_tc_scenario(index, latex_directory, "scenario-input-buffer-fill-level.tex", dictionary)


if __name__ == '__main__':
    if not os.path.exists("setup.json"):
        print("A valid setup.json file should exist")
        exit(1)
    directory = init()
    data = json.loads(open("setup.json", "r").read())
    tc_count = len(data["test_cases"])
    max_node_count = 0
    for tc in range(tc_count):
        max_node_count = max(max_node_count, int(data["test_cases"][tc]["node_count"]))
        build_tc_scenario_setup(tc, directory, data["test_cases"][tc])
        build_ts_scenario_buffer_fill_level(tc, directory, data["test_cases"][tc])
        # build_ts_scenario_input_buffer_usage(tc, directory, data["test_cases"][tc])
        build_ts_scenario_bandwidth(tc, directory, data["test_cases"][tc])
        build_ts_scenario_ts_completion_duration(tc, directory, data["test_cases"][tc])
        build_ts_scenario_input_buffer_fill_level(tc, directory, data["test_cases"][tc])
        append_built_scenario(tc, directory)

    build_setup_slide(directory, max_node_count)
    latex_path = "FLESnet.tex"
    os.system("cd %s && pdflatex  -synctex=1 -interaction=nonstopmode %s" % (directory, latex_path))
