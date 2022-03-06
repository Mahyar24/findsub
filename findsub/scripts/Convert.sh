#! /usr/bin/env bash

# Converting srt files to UTF-8.
# Mahyar@Mahyar24.com, Thu 19 Aug 2021.

cd "${1}" || exit 1;

for sub in *.srt; do
	type=$(file -b "${sub}");
	sub_name="${sub%%\.srt}";

    case "$type" in
        "Non-ISO extended-ASCII text, with CRLF line terminators" | "Non-ISO extended-ASCII text, with CRLF, NEL line terminators")
            iconv -f WINDOWS-1256 -t UTF-8 "${sub}" -o "${sub_name}_FIXED.srt";
            rm "${sub}";;
        "Little-endian UTF-16 Unicode text, with CRLF, CR line terminators")
            iconv -f UTF-16 -t UTF-8 "${sub}" -o "${sub_name}_FIXED.srt";
            rm "${sub}";;
        "Big-endian UTF-16 Unicode text, with CRLF line terminators")
            iconv -f UTF-16BE -t UTF-8 "${sub}" -o "${sub_name}_FIXED.srt";
            rm "${sub}";;
        *)
	        echo "${sub}" "is correct already!";;
	esac
done
