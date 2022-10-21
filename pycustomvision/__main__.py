from pycustomvision import CustomVisionClient
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--resource-name',  type=str, required=True)
    parser.add_argument('-p', '--project-id', type=str, required=True)
    parser.add_argument('-s', '--subscription-key', type=str, required=True)
    parser.add_argument('-o', '--output-dir', type=str, required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    client = CustomVisionClient(args.resource_name,
                                args.project_id,
                                args.subscription_key)
    client.export_dataset(args.output_dir)


if __name__ == '__main__':
    main()
