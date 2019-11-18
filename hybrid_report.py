from junitparser import *
import argparse
from shutil import copyfile, copytree
import os
import jinja2
import time


def env_override(value, key):
    return os.getenv(key, value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--xml_path', required=True)
    parser.add_argument('--images_basedir', required=True)
    parser.add_argument('--report_path', default=os.path.join(os.path.dirname(__file__), 'FailuresReport'))
    parser.add_argument('--report_name', default='report.html')

    args = parser.parse_args()

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

    for suite in xml:
        for case in suite:
            if case.result:
                img_name = case.result.message.splitlines()[-1]

                if not os.path.exists(os.path.join(args.images_basedir, ref_dir, img_name)) and not os.path.exists(os.path.join(args.images_basedir, out_dir, img_name)):
                    cases_list.append(case.name + img_name)
                else:
                    cases_list.append(img_name)
                    for target_dir in [ref_dir, out_dir]:
                        source_img_path = os.path.join(args.images_basedir, target_dir, img_name)
                        report_img_path = os.path.join(args.report_path, target_dir, img_name)
                        if os.path.exists(source_img_path):
                            try:
                                copyfile(source_img_path, report_img_path)
                            except OSError as err:
                                print(str(err))
                                print(img_name)

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('hybrid_report', 'templates'),
        autoescape=True
    )
    env.filters['env_override'] = env_override
    template = env.get_template('main_template.html')

    html_result = template.render(title="Title",
                                  cases_list=cases_list)

    with open(os.path.join(args.report_path, args.report_name), 'w') as html_file:
        html_file.write(html_result)

    copytree("resources", os.path.join(args.report_path, "report_resources"))


if __name__ == '__main__':
    main()
