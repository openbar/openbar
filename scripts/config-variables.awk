# Use a special output separator to let make(1) evaluate the output
# as the new line characters are substituted.
BEGIN				{ ORS = "\v" }

# Remove the separators between the printed strings and manage the spacing
# manually.
BEGIN				{ OFS = "" }

# Use colon as field separator to extract the targets.
BEGIN				{ FS = ":| " }

# Handle makefile errors.
/\*\*\*.*Stop\.$/		{ error = $0;
				  sub(/.*\*\*\*[[:space:]]+/, "", error);
				  sub(/\.[[:space:]]+Stop\.$/, "", error);
				  exit; }

# Handle multi-line variables.
/^define /			{ multiline = 1 }
/^endef$/			{ multiline = 0 }

# Variables are defined in a dedicated section surrounded by blank lines.
/^#[[:space:]]+Variables$/	{ variable_section = 2 }
/^$/				{ if (multiline == 0) variable_section-- }

# Only explicit variables are valid.
/^#[[:space:]]+makefile \(from '[[:print:]]+', line [[:digit:]]+\)$/ \
				{ variable = 1 }

# Also allow overridden variables.
/^#[[:space:]]+'override' directive \(from '[[:print:]]+', line [[:digit:]]+\)$/ \
				{ variable = 1; override = 1 }

# Explicit targets are defined in the Files section.
/^#[[:space:]]+Files$/		{ target_section = 1 }

# Not a target blocks are ignored.
/^#[[:space:]]+Not a target:$/	{ notatarget = 1 }
/^$/				{ notatarget = 0 }

# Comments and blank lines are skipped.
/^#/ || /^$/			{ if (multiline == 0) next }

# Special variables are ignored.
/^\.DEFAULT_GOAL/		|| \
/^\.EXTRA_PREREQS/		|| \
/^\.FEATURES/			|| \
/^\.INCLUDE_DIRS/		|| \
/^\.LIBPATTERNS/		|| \
/^\.LOADED/			|| \
/^\.RECIPEPREFIX/		|| \
/^\.SHELLFLAGS/			|| \
/^\.VARIABLES/			|| \
/^COMSPEC/			|| \
/^CURDIR/			|| \
/^DESTDIR/			|| \
/^GPATH/			|| \
/^MAKE/				|| \
/^MAKECMDGOALS/			|| \
/^MAKEFILES/			|| \
/^MAKEFILE_LIST/		|| \
/^MAKELEVEL/			|| \
/^MAKESHELL/			|| \
/^MAKE_HOST/			|| \
/^MAKE_RESTARTS/		|| \
/^MAKE_TERMERR/			|| \
/^MAKE_TERMOUT/			|| \
/^MAKE_VERSION/			|| \
/^MFLAGS/			|| \
/^OUTPUT_OPTION/		|| \
/^SHELL/			|| \
/^SUFFIXES/			|| \
/^VPATH/			{ if (multiline == 0) variable = 0 }

# Special targets are ignored.
/^\.PHONY:/			|| \
/^\.SUFFIXES:/			|| \
/^\.DEFAULT:/			|| \
/^\.PRECIOUS:/			|| \
/^\.INTERMEDIATE:/		|| \
/^\.SECONDARY:/			|| \
/^\.SECONDEXPANSION:/		|| \
/^\.DELETE_ON_ERROR:/		|| \
/^\.IGNORE:/			|| \
/^\.LOW_RESOLUTION_TIME:/	|| \
/^\.SILENT:/			|| \
/^\.EXPORT_ALL_VARIABLES:/	|| \
/^\.NOTPARALLEL:/		|| \
/^\.ONESHELL:/			|| \
/^\.POSIX:/			{ notatarget = 1 }

# Internal targets are ignored.
/^[[:print:]]*_defconfig:/	|| \
/^foreach:/			|| \
/^help:/			|| \
/^shell:/			{ notatarget = 1 }

# Recipes are skipped.
/^\t/				{ if (multiline == 0) next }

{
	# Remaining variables are printed.
	if (variable_section > 0) {
		if (override) {
			override = 0;

			print "override OB_EXPORT += " $1;

			if (OVERRIDE) {
				print "override " $0;
				print "export " $1;
			}

		} else if (variable) {
			print;
		}
	}

	# The next variable must be validated again.
	if (multiline == 0) variable = 0;

	# Remaining targets are saved.
	if (target_section > 0 && !notatarget) {
		targets[$1]++;
	}
}

# The saved targets are printed in a dedicated variable if no errors where
# detected.
END {
	if (error) {
		print "ifdef CONFIG_IGNORE_ERROR";
		print "  CONFIG_ERROR := ", error;
		print "else"
		print "  $(error .config: ", error, ")";
		print "endif";

	} else {
		printf "OB_ALL_TARGETS := ";

		for (target in targets) {
			printf " %s", target;
		}

		print "";
	}
}
