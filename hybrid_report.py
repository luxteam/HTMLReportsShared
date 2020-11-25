from junitparser import *
import argparse
from shutil import copyfile, copytree
import os
import jinja2
import time
from glob import glob


def env_override(value, key):
    return os.getenv(key, value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--xml_path', required=True)
    parser.add_argument('--images_basedir', required=True)
    parser.add_argument('--report_path', default=os.path.join(os.path.dirname(__file__), 'FailuresReport'))
    parser.add_argument('--report_name', default='report.html')
    parser.add_argument('--tool_name', default='Hybrid')
    parser.add_argument('--compare_with_refs', default='True')

    args = parser.parse_args()

    args.compare_with_refs = args.compare_with_refs == 'True'

    ref_dir = 'ReferenceImages'
    out_dir = 'OutputImages'

    xml = JUnitXml.fromfile(args.xml_path)
    cases_list = []

    try:
        if os.path.exists(args.report_path):
            print("Output folder already exists. Rename it.")
            localtime = time.localtime()
            os.rename(args.report_path,
                      args.report_path + "_{}_{}_{}".format(localtime.tm_hour, localtime.tm_min, localtime.tm_sec))

        os.makedirs(os.path.join(args.report_path, ref_dir))
        os.makedirs(os.path.join(args.report_path, out_dir))
    except OSError as err:
        print(str(err))
        exit(-1)

    images = []
    out_images = set(glob(os.path.join(args.images_basedir, out_dir, "*")))
    if args.compare_with_refs:
        ref_images = set(glob(os.path.join(args.images_basedir, ref_dir, "*")))
        for images_paths in [ref_images, out_images]:
            for image_path in images_paths:
                image = os.path.basename(image_path)
                if image not in images:
                    images.append(os.path.basename(image_path))
    else:
        for image_path in out_images:
            image = os.path.basename(image_path)
            if image not in images:
                images.append(os.path.basename(image_path))

    for suite in xml:
        for case in suite:
            if case.result:
                image_found = False
                for image in images:
                    if image.startswith(case.name):
                        cases_list.append(image)
                        image_found = True
                        if args.compare_with_refs:
                            target_dirs = [ref_dir, out_dir]
                        else:
                            target_dirs = [out_dir]
                        for target_dir in target_dirs:
                            source_img_path = os.path.join(args.images_basedir, target_dir, image)
                            report_img_path = os.path.join(args.report_path, target_dir, image)
                            if not os.path.exists(source_img_path):
                                source_img_path = os.path.join('resources', 'img', 'no-image.jpg')
                            try:
                                copyfile(source_img_path, report_img_path)
                            except OSError as err:
                                print(str(err))
                                print(image)
                if not image_found:
                    cases_list.append(case.name + '.png')

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('hybrid_report', 'templates'),
        autoescape=True
    )
    env.filters['env_override'] = env_override
    template = env.get_template('main_template.html')

    html_result = template.render(title="Title",
                                  cases_list=cases_list,
                                  tool_name=args.tool_name,
                                  compare_with_refs=args.compare_with_refs)

    with open(os.path.join(args.report_path, args.report_name), 'w') as html_file:
        html_file.write(html_result)

    copytree("resources", os.path.join(args.report_path, "report_resources"))


if __name__ == '__main__':
    main()
