import argparse
from shutil import copyfile, copytree
import os
import jinja2
import time
from glob import glob
import junitparser2


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

    if 'Core' in args.tool_name:
        missing_image_name = 'error.png'
        image_prefix = '4xDiff_'
    else:
        missing_image_name = 'no-image.png'
        image_prefix = ''

    if args.compare_with_refs:
        target_dirs = [ref_dir, out_dir]
    else:
        target_dirs = ['.']

    xml = junitparser2.JUnitXml.fromfile(args.xml_path)
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

    if not 'Hybrid' in args.tool_name:
        images = []
        if args.compare_with_refs:
            out_images = set(glob(os.path.join(args.images_basedir, out_dir, "*")))
            ref_images = set(glob(os.path.join(args.images_basedir, ref_dir, "*")))
            for images_paths in [ref_images, out_images]:
                for image_path in images_paths:
                    image = os.path.basename(image_path)
                    if image not in images:
                        images.append(os.path.basename(image_path))
        else:
            out_images = set(glob(os.path.join(args.images_basedir, "*")))
            for image_path in out_images:
                image = os.path.basename(image_path)
                if image not in images:
                    images.append(os.path.basename(image_path))

    for suite in xml:
        for case in suite:
            if case.result:
                image_found = False
                if not 'Hybrid' in args.tool_name:
                    # case.result is a list
                    # in Core we have only one image and failure reason per test
                    # Core generate only diff images so we take all images
                    try:
                        failure_reason = case.result[0]._elem.text
                    except:
                        failure_reason = "Unknown reason"

                    for image in images:
                        if image.startswith(image_prefix + case.name):
                            cases_list.append({'name': image, 'reason': failure_reason})
                            image_found = True
                            for target_dir in target_dirs:
                                source_img_path = os.path.join(args.images_basedir, target_dir, image)
                                if not os.path.exists(source_img_path):
                                    source_img_path = os.path.join('resources', 'img', missing_image_name)
                                # save images not in root of dir with html report
                                dir_to_save = out_dir if target_dir == '.' else target_dir
                                report_img_path = os.path.join(args.report_path, dir_to_save, image)
                                try:
                                    copyfile(source_img_path, report_img_path)
                                except OSError as err:
                                    print(str(err))
                                    print(image)
                else:   
                    # Take images from failure reasons 
                    # In Hybrid we can have multiple images for one case    
                    image_found = True
                    for result in case.result:
                        try:
                            failure_reason = result._elem.text
                        except:
                            failure_reason = "Unknown reason"
                        img_name = result.message.splitlines()[-1]
                        # check that image name is name of image (Not just a sentence of error message)
                        # + check that image doesn't exist in refs and output dirs (it means that name of target image is case name + img_name)
                        if " " not in img_name and not os.path.exists(os.path.join(args.images_basedir, ref_dir, img_name)) and not os.path.exists(os.path.join(args.images_basedir, out_dir, img_name)):
                            cases_list.append({'name': case.name + img_name, 'reason': failure_reason})
                        else:
                            if " " in img_name:
                                img_name = case.name
                            cases_list.append({'name': img_name, 'reason': failure_reason})
                            for target_dir in [ref_dir, out_dir]:
                                source_img_path = os.path.join(args.images_basedir, target_dir, img_name)
                                if not os.path.exists(source_img_path):
                                        source_img_path = os.path.join('resources', 'img', missing_image_name)
                                report_img_path = os.path.join(args.report_path, target_dir, img_name)
                                if os.path.exists(source_img_path):
                                    try:
                                        copyfile(source_img_path, report_img_path)
                                    except OSError as err:
                                        print(str(err))
                                        print(img_name)
                if not image_found:
                    for target_dir in target_dirs:
                        source_img_path = os.path.join('resources', 'img', missing_image_name)
                        # save images not in root of dir with html report
                        dir_to_save = out_dir if target_dir == '.' else target_dir
                        report_img_path = os.path.join(args.report_path, dir_to_save, case.name + '.png')
                        try:
                            copyfile(source_img_path, report_img_path)
                        except OSError as err:
                            print(str(err))
                            print(case.name)
                    cases_list.append({'name': case.name + '.png', 'reason': failure_reason})

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
