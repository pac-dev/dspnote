from .project import Project
import sys, logging, argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('subcommand', choices=['serve', 'build'])
	parser.add_argument('source_dir', help='path to dspnote project')
	args = parser.parse_args()
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
	proj = Project(source_dir=args.source_dir)
	match args.subcommand:
		case 'serve': return proj.serve()
		case 'build': return proj.generate()

if __name__ == '__main__':
	sys.exit(main())
