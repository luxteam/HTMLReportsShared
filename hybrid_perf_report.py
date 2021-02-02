import argparse
from shutil import copyfile, copytree
import os
import jinja2
import time
from glob import glob
import json


def env_override(value, key):
    return os.getenv(key, value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_files_path', required=True)
    parser.add_argument('--report_path', default=os.path.join(os.path.dirname(__file__), 'PerformanceReport'))

    args = parser.parse_args()

    os.makedirs(os.path.join(args.report_path))

    metrics_list = {}
    platforms = set(glob(os.path.join(args.json_files_path, "*")))
    # go through platforms
    for platform_path in platforms:
        current_platform = {"reports": {}, "summary": {"passed": 0, "warning": 0, "error": 0, "total": 0}}
        # formatted platform name which will be displayed in report
        platform_name = os.path.split(platform_path)[1].replace("_", " ").replace("-", " (") + ")"
        current_platform["name"] = platform_name
        metrics_list[os.path.split(platform_path)[1]] = current_platform
        reports = set(glob(os.path.join(platform_path, "*")))
        # go through json reports
        for report in reports:
            with open(report) as file:
                metrics = json.load(file)
                report_name = os.path.split(report)[1].replace("_", " ").replace(".json", "").replace(r"^Report", "")
                current_report = {"name": report_name, "metrics": {}, "summary": {"passed": 0, "warning": 0, "error": 0, "total": 0}}
                current_platform["reports"][os.path.split(report)[1].replace(".json", "")] = current_report
                for metric in metrics:
                    current_report["metrics"][metric] = metrics[metric]
                    # Presence of 'Cliff detected' field means that metric contains error
                    if "Cliff_detected" in metrics[metric] and metrics[metric]["Cliff_detected"]:
                        status = "error"
                    # Presence of 'Unexpected acceleration' field means that metric contains warning
                    elif "Unexpected_acceleration" in metrics[metric] and metrics[metric]["Unexpected_acceleration"]:
                        status = "warning"
                    else:
                        status = "passed"
                    current_report["metrics"][metric]["status"] = status
                    current_report["summary"][status] += 1
                    current_report["summary"]["total"] += 1

                for status in current_report["summary"]:
                    current_platform["summary"][status] += current_report["summary"][status]

    # save json report
    with open(os.path.join(args.report_path, "performace_report.json"), "w", encoding="utf8") as file:
        json.dump(metrics_list, file, indent=4, sort_keys=True)

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('hybrid_report', 'templates'),
        autoescape=True
    )
    env.filters["env_override"] = env_override
    # build main performance report
    template = env.get_template("perf_template.html")

    html_result = template.render(title="Hybrid Performace Tests", metrics_list=metrics_list)

    with open(os.path.join(args.report_path, "performace_report.html"), "w") as html_file:
        html_file.write(html_result)

    # build report with metrics for each json report
    for platform in metrics_list:
        platform_path = os.path.join(args.report_path, platform)
        os.makedirs(platform_path)
        reports = metrics_list[platform]["reports"]
        for report_name, report_data in reports.items():
            template = env.get_template("perf_template_report.html")
            html_result = template.render(title="Hybrid Performace Tests ({})".format(report_name), report=report_data)
            with open(os.path.join(platform_path, report_name + ".html"), "w") as html_file:
                html_file.write(html_result)

    copytree("resources", os.path.join(args.report_path, "report_resources"))


if __name__ == '__main__':
    main()
