#! /bin/bash

# Converting srt files to UTF-8.
# Mahyar@Mahyar24.com, Thu 19 Aug 2021.


cd "${1}" || exit 1;

for sub in *.srt; do
	type=$(file -b "${sub}");
	sub_name="${sub%%\.srt}";

	if [[ "$type" == "Non-ISO extended-ASCII text, with CRLF line terminators" ]]; then
	    iconv -f WINDOWS-1256 -t UTF-8 "${sub}" -o "${sub_name}_FIXED.srt";
	    rm "${sub}";
	elif [[ "$type" == "Little-endian UTF-16 Unicode text, with CRLF, CR line terminators" ]]; then
	    iconv -f UTF-16 -t UTF-8 "${sub}" -o "${sub_name}_FIXED.srt";
	    rm "${sub}";
	elif [[ "$type" == "Big-endian UTF-16 Unicode text, with CRLF line terminators" ]]; then
	    iconv -f UTF-16BE -t UTF-8 "${sub}" -o "${sub_name}_FIXED.srt";
	    rm "${sub}";
	else
	    echo "${sub}" "is correct already!";
	fi
done
