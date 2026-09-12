import ast
import math
import operator
import re

# ===================== KÜRESEL HASSASİYET =====================
# Tüm CORDIC tabanlı hesaplamalarda kullanılacak iterasyon sayısı
PREC = 40

# ===================== CORDIC SINIFI =====================
class Cordic:
    def __init__(self, cord=1):
        self.coordinate = cord

    def romValuePerIteration(self, i):
        if self.coordinate == 1:
            return math.atan(2**(-i))
        elif self.coordinate == -1:
            return math.atanh(2**(-i))
        else:
            return 2**(-i)

    def simpleshift(self, x, d, i):
        return d * x * (2**(-i))

    def iteration(self, x, y, z, mode, ROMval, i, compareVal):
        x0 = x
        if mode:
            d = -1 if z < compareVal else 1
        else:
            d = 1 if y < compareVal else -1
        x = x0 - self.coordinate * self.simpleshift(y, d, i)
        y = y + self.simpleshift(x0, d, i)
        z = z - d * ROMval
        return x, y, z

    def iterations(self, x, y, z, mode, numIters, compareVal):
        i = 1 if self.coordinate == -1 else 0
        k_hyp = 4 if self.coordinate == -1 else -1
        while i < numIters:
            ROMval = self.romValuePerIteration(i)
            x, y, z = self.iteration(x, y, z, mode, ROMval, i, compareVal)
            if i == k_hyp:
                k_hyp = 3 * k_hyp + 1
            else:
                i += 1
        return x, y, z

    def rotation(self, x, y, z, numIters, compareVal=0):
        return self.iterations(x, y, z, True, numIters, compareVal)

    def vectoring(self, x, y, z, numIters, compareVal=0):
        return self.iterations(x, y, z, False, numIters, compareVal)

# ===================== TRIGONOMETRİK =====================
class TrigonometricFunction:
    def __init__(self, iters=PREC):
        self.cordic = Cordic()
        self.iters = iters
        # K çarpanı iterasyon sayısına göre
        gain_val = math.sqrt(2)
        for i in range(1, iters):
            gain_val *= math.sqrt(1 + 2**(-2 * i))
        self.K = 1 / gain_val

    def sincos(self, theta, iterations=None):
        iterations = self.iters if iterations is None else iterations
        t = ((theta + math.pi) % (2 * math.pi)) - math.pi
        if t > math.pi / 2:
            alpha = math.pi - t
            s_s, s_c = 1, -1
        elif t < -math.pi / 2:
            alpha = t + math.pi
            s_s, s_c = -1, -1
        else:
            alpha = t
            s_s, s_c = 1, 1
        x, y, _ = self.cordic.rotation(self.K, 0, alpha, iterations)
        return x * s_c, y * s_s  # (cos, sin)

    def sin(self, theta, iterations=None): 
        return self.sincos(theta, iterations)[1]
    def cos(self, theta, iterations=None): 
        return self.sincos(theta, iterations)[0]

    def tan(self, theta, iterations=None):
        iterations = self.iters if iterations is None else iterations
        c, s = self.sincos(theta, iterations)
        if abs(c) < 1e-6:
            raise ValueError("tanımsız")
        return s / c

    def sec(self, theta, iterations=None):
        iterations = self.iters if iterations is None else iterations
        c = self.cos(theta, iterations)
        if abs(c) < 1e-6:
            raise ValueError("tanımsız")
        return 1.0 / c

    def csc(self, theta, iterations=None):
        iterations = self.iters if iterations is None else iterations
        s = self.sin(theta, iterations)
        if abs(s) < 1e-6:
            raise ValueError("tanımsız")
        return 1.0 / s

    def cot(self, theta, iterations=None):
        iterations = self.iters if iterations is None else iterations
        s = self.sin(theta, iterations)
        c = self.cos(theta, iterations)
        if abs(s) < 1e-6:
            raise ValueError("tanımsız")
        return c / s

    # ======== Ters trig (arc) (çıktı rad) ========
    def arcsin(self, val, iterations=None):
        iterations = self.iters if iterations is None else iterations
        if not -1 <= val <= 1:
            raise ValueError("arcsin tanımsız (|x| > 1)")
        if abs(val) == 1.0:
            return math.copysign(math.pi/2, val)
        x0 = math.sqrt(max(0.0, 1.0 - val*val))
        _, _, z = self.cordic.vectoring(x0, val, 0.0, iterations)
        return z

    def arccos(self, val, iterations=None):
        iterations = self.iters if iterations is None else iterations
        if not -1 <= val <= 1:
            raise ValueError("arccos tanımsız (|x| > 1)")
        return math.pi/2 - self.arcsin(val, iterations)

    def arctan(self, val, iterations=None):
        iterations = self.iters if iterations is None else iterations
        _, _, z = self.cordic.vectoring(1.0, val, 0.0, iterations)
        return z

    def arccot(self, val, iterations=None):
        iterations = self.iters if iterations is None else iterations
        return math.pi/2 - self.arctan(val, iterations)

    def arcsec(self, val, iterations=None):
        iterations = self.iters if iterations is None else iterations
        if abs(val) < 1:
            raise ValueError("arcsec tanımsız (|x| < 1)")
        return self.arccos(1.0/val, iterations)

    def arccsc(self, val, iterations=None):
        iterations = self.iters if iterations is None else iterations
        if abs(val) < 1:
            raise ValueError("arccsc tanımsız (|x| < 1)")
        return self.arcsin(1.0/val, iterations)

# ===================== HİPERBOLİK =====================
class HyperbolicFunction:
    def __init__(self, iters=PREC):
        self.cordic = Cordic(-1)
        self.iters = iters
        # --- Kh (ölçek) ve ulaşılabilir açı toplamı (Amax) ---
        gain = 1.0
        Amax = 0.0
        i, k = 1, 4
        while i < iters:
            term = 1.0 - 2.0**(-2*i)
            if term > 0:
                gain *= math.sqrt(term)
            Amax += math.atanh(2.0**(-i))
            if i == k:
                # hiperbolikte tekrar: aynı i bir kez daha
                gain *= math.sqrt(term)
                Amax += math.atanh(2.0**(-i))
                k = 3*k + 1
            else:
                i += 1
        self.Kh = 1.0 / gain      # başlangıç x
        self.Amax = Amax          # yakınsama aralığı ~1.118...

    def _cosh_sinh_cordic(self, a, iterations=None):
        iterations = self.iters if iterations is None else iterations
        x, y, _ = self.cordic.rotation(self.Kh, 0.0, a, iterations)
        return x, y  # (cosh, sinh)

    def cosh_sinh(self, a, iterations=None):
        iterations = self.iters if iterations is None else iterations
        # --- Aralık küçültme: |a| > Amax ise 2^m ile küçült ---
        aa = float(a)
        if aa == 0.0:
            return 1.0, 0.0
        m = 0
        A = abs(aa)
        while A > self.Amax:
            A *= 0.5
            m += 1
        a_red = math.copysign(A, aa)

        # CORDIC çekirdeğiyle küçük açıda cosh/sinh
        c, s = self._cosh_sinh_cordic(a_red, iterations)

        # --- İkiye katlama ile geri büyüt ---
        for _ in range(m):
            c, s = 2.0 * c * c - 1.0, 2.0 * s * c
        return c, s

    def cosh(self, a, iterations=None): 
        return self.cosh_sinh(a, iterations)[0]

    def sinh(self, a, iterations=None): 
        return self.cosh_sinh(a, iterations)[1]

    def tanh(self, a, iterations=None):
        c, s = self.cosh_sinh(a, iterations)
        if abs(c) < 1e-12:
            raise ValueError("tanh tanımsız (cosh≈0)")
        return s / c

    def sech(self, a, iterations=None):
        c = self.cosh(a, iterations)
        if abs(c) < 1e-12:
            raise ValueError("sech tanımsız (cosh≈0)")
        return 1.0 / c

    def csch(self, a, iterations=None):
        s = self.sinh(a, iterations)
        if abs(s) < 1e-12:
            raise ValueError("csch tanımsız (sinh≈0)")
        return 1.0 / s

    def coth(self, a, iterations=None):
        s = self.sinh(a, iterations)
        if abs(s) < 1e-12:
            raise ValueError("coth tanımsız (sinh≈0)")
        c = self.cosh(a, iterations)
        return c / s

    # --- Ters hiperbolikler (log ile) ---
    def arsinh(self, x, iterations=None):
        iterations = self.iters if iterations is None else iterations
        return MathFunctions().ln(x + math.sqrt(x*x + 1.0), iterations)

    def arcosh(self, x, iterations=None):
        iterations = self.iters if iterations is None else iterations
        if x < 1.0:
            raise ValueError("arcosh tanımsız (x < 1)")
        return MathFunctions().ln(x + math.sqrt((x - 1.0) * (x + 1.0)), iterations)

    def artanh(self, x, iterations=None):
        iterations = self.iters if iterations is None else iterations
        if not (-1.0 < x < 1.0):
            raise ValueError("artanh tanımsız (|x| >= 1) — sadece -1 < x < 1 aralığında tanımlı")
        mf = MathFunctions()
        return 0.5 * (mf.ln(1.0 + x, iterations) - mf.ln(1.0 - x, iterations))

# ===================== LOGARİTMA =====================
class MathFunctions:
    def __init__(self):
        self.hyperbolic = Cordic(-1)

    def ln(self, v, iterations=PREC):
        if v <= 0:
            raise ValueError("Pozitif sayı girilmeli.")
        k = 0
        while v >= 2:
            v /= 2
            k += 1
        while v < 0.5:
            v *= 2
            k -= 1
        _, _, z = self.hyperbolic.vectoring(v + 1, v - 1, 0, iterations)
        return 2 * z + k * math.log(2)

    def logtaban(self, v, base, iterations=PREC):
        if base <= 0 or base == 1:
            raise ValueError("Logaritma tabanı pozitif ve 1'den farklı olmalıdır.")
        return self.ln(v, iterations) / self.ln(base, iterations)

# ===================== ÖLÇÜM HAVUZU =====================
class MeasurementPool:
    def __init__(self):
        self.pool = []

    def add(self, value):
        self.pool.append(value)
        print(f"Sonuç: {value} (ölçüm #{len(self.pool)-1})")

    def list(self):
        if not self.pool:
            print("Ölçüm havuzu boş.")
        for i, v in enumerate(self.pool):
            print(f"[{i}] {v}")

    def clear(self):
        self.pool.clear()
        print("Havuz temizlendi.")

# ===================== HELP / TANIM ARALIKLARI =====================
def print_domain_help():
    txt = r"""
=== Fonksiyon Tanım Aralıkları ===

[Trig]
  sin(x), cos(x):       x ∈ ℝ
  tan(x), sec(x):       x ≠ π/2 + kπ
  cot(x), csc(x):       x ≠ kπ

[Ters Trig]
  arcsin(x):            -1 ≤ x ≤ 1
  arccos(x):            -1 ≤ x ≤ 1
  arctan(x):            x ∈ ℝ
  arccot(x):            x ∈ ℝ
  arcsec(x):            |x| ≥ 1
  arccsc(x):            |x| ≥ 1

[Hiperbolik]
  sinh(x), cosh(x):     x ∈ ℝ
  tanh(x):              x ∈ ℝ
  coth(x), csch(x):     x ≠ 0
  sech(x):              x ∈ ℝ

[Ters Hiperbolik]
  arsinh(x):            x ∈ ℝ
  arcosh(x):            x ≥ 1
  artanh(x):            -1 < x < 1

[Log]
  ln(x):                x > 0
  logtaban(x, b):       x > 0, b > 0, b ≠ 1
"""
    print(txt)

# ===================== GÜVENLİ İFADE AYRIŞTIRICI =====================
class SafeExpressionEvaluator:
    """Yalnızca izinli sayısal işlemleri ve fonksiyonları değerlendirir."""

    MAX_EXPRESSION_LENGTH = 500
    MAX_AST_NODES = 100
    MAX_ABS_VALUE = 1e100
    MAX_ABS_EXPONENT = 100

    binary_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    unary_operators = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def __init__(self, allowed_names):
        self.allowed_names = allowed_names

    def evaluate(self, expression: str) -> float:
        if not expression or len(expression) > self.MAX_EXPRESSION_LENGTH:
            raise ValueError("İfade boş veya çok uzun.")
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise ValueError("Geçersiz ifade.") from exc
        if sum(1 for _ in ast.walk(tree)) > self.MAX_AST_NODES:
            raise ValueError("İfade çok karmaşık.")
        return float(self._evaluate_node(tree.body))

    def _evaluate_node(self, node):
        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Yalnızca sayısal sabitler kullanılabilir.")
            return self._validate_number(node.value)

        if isinstance(node, ast.Name):
            value = self.allowed_names.get(node.id)
            if value is None or callable(value):
                raise ValueError(f"İzin verilmeyen ad: {node.id}")
            return self._validate_number(value)

        if isinstance(node, ast.UnaryOp) and type(node.op) in self.unary_operators:
            result = self.unary_operators[type(node.op)](self._evaluate_node(node.operand))
            return self._validate_number(result)

        if isinstance(node, ast.BinOp) and type(node.op) in self.binary_operators:
            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > self.MAX_ABS_EXPONENT:
                raise ValueError("Üs değeri çok büyük.")
            try:
                result = self.binary_operators[type(node.op)](left, right)
            except (ArithmeticError, OverflowError) as exc:
                raise ValueError("İşlem hesaplanamadı.") from exc
            return self._validate_number(result)

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.keywords:
                raise ValueError("Yalnızca izinli fonksiyon çağrıları kullanılabilir.")
            function = self.allowed_names.get(node.func.id)
            if not callable(function):
                raise ValueError(f"İzin verilmeyen fonksiyon: {node.func.id}")
            arguments = [self._evaluate_node(argument) for argument in node.args]
            try:
                return self._validate_number(function(*arguments))
            except TypeError as exc:
                raise ValueError("Fonksiyon için geçersiz sayıda argüman verildi.") from exc

        raise ValueError("İfadede izin verilmeyen bir yapı var.")

    def _validate_number(self, value):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("Sonuç sonlu bir sayı olmalıdır.")
        if abs(value) > self.MAX_ABS_VALUE:
            raise ValueError("Sayısal değer çok büyük.")
        return value


# ===================== PARSE =====================
def auto_insert_parentheses(expr: str) -> str:
    pattern = (
        r'(?<![a-zA-Z0-9_])'
        r'(?P<func>'
        r'arcsin|arccos|arctan|arccot|arcsec|arccsc|'
        r'arsinh|arcosh|artanh|'
        r'sin|cos|tan|cot|sec|csc|'
        r'sinh|cosh|tanh|coth|sech|csch'
        r')'
        r'(?P<val>-?\d+(\.\d+)?)(?!\w)'
    )
    return re.sub(pattern, r'\g<func>(\g<val>)', expr)

def parse_angle(value: float, mode: str) -> float:
    value = float(value)
    return math.radians(value) if mode == "deg" else value

def eval_expression(expr: str, angle_mode: str,
                    trig: TrigonometricFunction,
                    hyp: HyperbolicFunction,
                    mathf: MathFunctions) -> float:
    expr = auto_insert_parentheses(expr.lower().replace("^", "**"))

    def trig_wrap(fname):
        return lambda x: getattr(trig, fname)(parse_angle(x, angle_mode), PREC)

    def arc_wrap(fname):
        def f(x):
            rad = getattr(trig, fname)(float(x), PREC)
            return math.degrees(rad) if angle_mode == "deg" else rad
        return f

    def hyp_wrap(fname):
        return lambda x: getattr(hyp, fname)(float(x), PREC)

    allowed = {
        # trig
        "sin": trig_wrap("sin"), "cos": trig_wrap("cos"),
        "tan": trig_wrap("tan"), "cot": trig_wrap("cot"),
        "sec": trig_wrap("sec"), "csc": trig_wrap("csc"),
        # arc-trig
        "arcsin": arc_wrap("arcsin"), "arccos": arc_wrap("arccos"),
        "arctan": arc_wrap("arctan"), "arccot": arc_wrap("arccot"),
        "arcsec": arc_wrap("arcsec"), "arccsc": arc_wrap("arccsc"),
        # hyperbolic
        "sinh": hyp_wrap("sinh"), "cosh": hyp_wrap("cosh"),
        "tanh": hyp_wrap("tanh"), "coth": hyp_wrap("coth"),
        "sech": hyp_wrap("sech"), "csch": hyp_wrap("csch"),
        # inverse hyperbolic (çıktı sayı)
        "arsinh": hyp_wrap("arsinh"),
        "arcosh": hyp_wrap("arcosh"),
        "artanh": hyp_wrap("artanh"),
        # log
        "ln": lambda x: mathf.ln(x, PREC),
        "logtaban": lambda x, base: mathf.logtaban(x, base, PREC),
        # sabitler
        "pi": math.pi, "e": math.e,
    }

    return SafeExpressionEvaluator(allowed).evaluate(expr)

# ===================== ANA PROGRAM =====================
if __name__ == "__main__":
    trig = TrigonometricFunction(PREC)
    hyp  = HyperbolicFunction(PREC)
    mathf = MathFunctions()
    pool = MeasurementPool()
    angle_mode = "none"

    print("CORDIC Hesap Makinesi (Trig, Ters Trig, Hiperbolik, Log)")
    print(f"Iterasyon (PREC): {PREC}")
    print("Açı modu: mode deg | mode rad | mode none")
    print('Yardım: "help" veya "yardım"')
    print("Örnekler:")
    print("  sin30 + cos60")
    print("  arcsin0.5 + arctan1")
    print("  sinh1 + cosh0.5")
    print("  tanh(0.3) + arsinh(2)")
    print("  2*tan45 + logtaban(8,2)")
    print("  ölçüm[0] + 3 * ölçüm[1]")
    print("Komutlar: list | clear | q\n")

    while True:
        try:
            inp = input(f"[{angle_mode.upper()}] > ").strip().lower()

            if inp == "q":
                break
            elif inp in ("help", "yardım"):
                print_domain_help(); continue
            elif inp.startswith("mode "):
                mode_cmd = inp.split(" ", 1)[1]
                if mode_cmd in ("deg", "rad", "none"):
                    angle_mode = mode_cmd
                    print(f"Açı modu değiştirildi: {angle_mode}")
                else:
                    print("Geçersiz açı modu.")
                continue
            elif inp == "list":
                pool.list(); continue
            elif inp == "clear":
                pool.clear(); continue
            elif "ölçüm[" in inp:
                inp = re.sub(r"ölçüm\[(\d+)\]", lambda m: str(pool.pool[int(m.group(1))]), inp)

            result = eval_expression(inp, angle_mode, trig, hyp, mathf)
            pool.add(result)

        except Exception as e:
            print("Hata:", e)
            print('(İpucu: "help" yazarak fonksiyonların tanım aralıklarını görebilirsiniz.)')
