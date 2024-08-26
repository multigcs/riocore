#!/usr/bin/env python3
#
#

import argparse
import os

import riocore

riocore_path = os.path.dirname(riocore.__file__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="json config file", nargs="?", type=str, default=None)
    parser.add_argument("output", help="output directory", nargs="?", type=str, default=None)
    parser.add_argument("--preview", "-p", help="generate preview / no pll config", default=False, action="store_true")
    parser.add_argument("--build", "-b", help="build gateware", default=False, action="store_true")
    parser.add_argument("--flash", "-f", help="flash gateware", default=False, action="store_true")
    args = parser.parse_args()

    if args.config:
        if args.config.endswith(".json"):
            if os.path.isfile(args.config):
                config_file = args.config
            elif os.path.isfile(f"{riocore_path}/configs/{args.config}"):
                config_file = f"{riocore_path}/configs/{args.config}"
            else:
                print(f"can not load: {args.config}")
                exit(1)
            print(f"loading: {config_file}")
            project = riocore.Project(config_file, args.output)
            project.generator(preview=args.preview)

            config_name = project.config.get("name")

            if args.build:
                cmd = f"(cd Output/{config_name}/Gateware/ ; make clean all)"
                print("")
                print("running:")
                print(f"  {cmd}")
                print("")
                os.system(cmd)
            if args.flash:
                cmd = f"(cd Output/{config_name}/Gateware/ ; make load)"
                print("")
                print("running:")
                print(f"  {cmd}")
                print("")
                os.system(cmd)

        elif args.config.startswith("testbench:"):
            plugin = args.config.split(":")[-1]
            plugins = riocore.Plugins()
            plugin_instance = plugins.load_plugin(plugin, {"type": plugin}, {"speed": 1000000, "jdata": {"clock": {"speed": 1000000}}})
            plugins.testbench_builder(plugin, plugin_instance)

        elif args.config.startswith("plugininfo:"):
            plugin = args.config.split(":")[-1]
            plugins = riocore.Plugins()
            print(plugins.info(plugin))

        elif args.config.startswith("pluginlist"):
            plugin = args.config.split(":")[-1]
            plugins = riocore.Plugins()
            for line in plugins.list():
                print(line)


if __name__ == '__main__':
    main()