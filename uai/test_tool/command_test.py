import argparse

from uai.deploy.tf_tool import TFDeployTool
from uai.pack.tf_pack_tool import TFPackTool

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='AI TensorFlow Arch Commander',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    tf_pack_tool = TFPackTool(parser)
    tf_pack_tool.pack()
    tf_deploy_tool = TFDeployTool(parser)
    tf_deploy_tool.deploy()
