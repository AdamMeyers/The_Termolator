import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from summary.term_generator import tchunk_to_terms


ROOT = Path(__file__).resolve().parents[1]
LEGACY = os.environ.get("TERMOLATOR_LEGACY")


class ChinesePipelineTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="termolator regression ")
        self.addCleanup(directory.cleanup)
        self.work = Path(directory.name)

    def write(self, name, content):
        path = self.work / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def command(self, *args):
        return subprocess.check_output(args, cwd=self.work)

    def test_accessor_variety_matches_complete_token_spans(self):
        ranked = self.write(
            "ranked", "\ufeff音频 信号\t10\n候选\t9\n未 命中\t8\n"
            "只有 右侧\t7\n只有 左侧\t6\n音频 信号\t5\n",
        )
        files = []
        for index, left, right in [(1, "左一", "右一"), (2, "左二", "右二"), (3, "左三", "右三")]:
            words = ["只有", "右侧", right, left + "!", "音频", "信号", right + '"',
                     left, "候选", right, "未", "不连续", "命中", left, "只有", "左侧"]
            files.append(self.write(f"{index}.tchunk", "".join(f"{word}\tNN\n" for word in words)))
        listing = self.write("chunks", "".join(f"{path}\n" for path in files))
        result = self.command(sys.executable, ROOT / "accessorvariety.py", ranked, listing)
        self.assertEqual(result, "音频 信号\t10\n候选\t9\n音频 信号\t5\n".encode())

    def test_chinese_map_preserves_source_offsets_for_multi_token_terms(self):
        sources = []
        chunks = []
        for index in range(3):
            # The embedded occurrence in 原音频 has the same characters but
            # a different token boundary. The space inside the final hit
            # still counts toward its source offsets.
            source = self.write(f"{index}.txt", "原音频信号。音频信号。音频 信号")
            chunk = self.write(
                f"{source.name}.tchunk",
                "".join(f"{word}\tNN\n" for word in
                        ["原音频", "信号", "。", "音频", "信号", "。", "音频", "信号"]),
            )
            sources.append(source.name)
            chunks.append(chunk.name)
        self.write("sources", "\n".join(sources) + "\n")
        self.write("chunks", "\n".join(chunks) + "\n")
        self.write("ranked", "音频 信号\n")
        self.command("sh", ROOT / "run_term_map.sh", "sources", "ranked", "sample", ".", ROOT, "zh", "chunks")
        mapped = (self.work / "sample.term_instance_map").read_text(encoding="utf-8")
        self.assertIn('number_of_files_containing_term=3 total_frequency=6', mapped)
        self.assertIn('<instance file="0" start=6 end=9/>', mapped)
        self.assertIn('<instance file="0" start=11 end=15/>', mapped)
        self.assertNotIn('start=1 end=', mapped)
        self.assertEqual((self.work / "sample.edited_term_list").read_text(encoding="utf-8"), "音频 信号\n")

    def test_cached_terms_keep_ids_order_frequency_and_inclusive_offsets(self):
        source = self.write("source.txt", "哈哈哈Aa哈哈")
        chunks = self.write("source.txt.tchunk", "哈哈\tNN\nAa\tNN\n哈哈\tNN\n\tO\n")
        tchunk_to_terms(source.as_posix(), chunks, self.work, "source.terms")
        expected = [
            ("哈哈", "哈哈", 2, 0, 1), ("哈哈", "哈哈", 2, 5, 6),
            ("Aa", "AA", 1, 3, 4),
            ("哈哈", "哈哈", 2, 0, 1), ("哈哈", "哈哈", 2, 5, 6),
        ]
        result = (self.work / "source.terms").read_bytes()
        self.assertEqual(result, "".join(
            f'TERM ID="NYU_TERM_{index}" STRING="{word}" LEMMA="{lemma}" FREQUENCY="{freq}" START={start} END={end}\n'
            for index, (word, lemma, freq, start, end) in enumerate(expected, 1)
        ).encode())
        if LEGACY:
            self.legacy_generate(source, chunks, "legacy.terms")
            self.assertEqual(result, (self.work / "legacy.terms").read_bytes())

    def legacy_generate(self, source, chunk, name):
        self.command(sys.executable, "-c",
                     "import sys; sys.path.insert(0, sys.argv[1]); "
                     "from term_generator import tchunk_to_terms; tchunk_to_terms(*sys.argv[2:])",
                     LEGACY, source, chunk, self.work, name)

    def test_chinese_map_matches_file_based_mapper_and_rebuilds(self):
        sources = []
        chunks = []
        term_files = []
        for index in range(3):
            stem = f"输入 {index}"
            extra = " 仅两篇" if index < 2 else ""
            source = self.write(stem + ".txt", "材料材料材 Material 材料 ß x" + extra)
            chunk = self.write("chunks/" + stem + ".txt.tchunk",
                               "材料\tNN\nMaterial\tNN\n材料\tNN\n仅两篇\tNN\nß x\tNN\n")
            sources.append(source.name)
            chunks.append(chunk.relative_to(self.work).as_posix())
            term_files.append(stem + ".terms")
            if LEGACY:
                self.legacy_generate(source, chunk, term_files[-1])
            else:
                tchunk_to_terms(source.as_posix(), chunk, self.work, term_files[-1])

        for filename, paths in [("source-list", sources), ("chunk-list", chunks), ("terms-list", term_files)]:
            self.write(filename, "\n".join(paths) + "\n")
        self.write("ranked", "基\n基 准 多\tss x\n材料\tmaterial\n仅两篇\n")
        if LEGACY:
            self.command(sys.executable, "-c",
                         "import sys; sys.path.insert(0, sys.argv[1]); "
                         "from get_term_maps import get_term_maps; get_term_maps(*sys.argv[2:])",
                         LEGACY, "ranked", "terms-list", "reference.map", ".")
        else:
            self.command(sys.executable, ROOT / "run_term_map.py", "ranked", "terms-list", "reference.map", ".")

        self.write("sample.term_instance_map", "stale\n")
        self.command("sh", ROOT / "run_term_map.sh", "source-list", "ranked", "sample", ".", ROOT, "zh", "chunk-list")
        mapped = (self.work / "sample.term_instance_map").read_text(encoding="utf-8")
        self.assertEqual(mapped, (self.work / "reference.map").read_text(encoding="utf-8"))
        self.assertIn('variants="基|ß" substring_of="基 准 多"', mapped)
        self.assertIn('total_frequency=21 variants="材料|material"', mapped)
        self.assertNotIn('string="仅两篇"', mapped)
        self.assertEqual((self.work / "sample.edited_term_list").read_bytes(),
                         "基|ß\n基 准 多|ß x\n材料|material\n".encode())


if __name__ == "__main__":
    unittest.main()
