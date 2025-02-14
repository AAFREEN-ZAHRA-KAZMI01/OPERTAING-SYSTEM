import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import time
import random

# Constants
NUM_PAGES = 15
NUM_FRAMES = 10
REPLACEMENT_ALGORITHMS = ["FIFO", "Optimal", "LRU"]
REFERENCE_STRING = [random.randint(0, NUM_PAGES - 1) for _ in range(19)]  # 10 references

# Class Definitions
class VirtualMemoryManager:
    def __init__(self):
        self.pages = [f"Page {i+1}" for i in range(NUM_PAGES)]
        self.frames = [None for _ in range(NUM_FRAMES)]
        self.page_table = {}
        self.virtual_to_physical_map = {}
        self.replacement_history = []
        self.fifo_queue = []
        self.lru_stack = []
        self.replacement_algo_index = 0
        self.allocation_table = []  # To store allocation details
        self.page_faults = 0
        self.page_hits = 0

    def allocate(self):
        print("Loading Data and Dividing into Pages...")
        self.visualize_initial_pages()
        time.sleep(2)

        print("\nReference String for Page Requests:", [self.pages[ref] for ref in REFERENCE_STRING])

        for ref in REFERENCE_STRING:
            page = self.pages[ref]
            print(f"\nProcessing {page}...")
            time.sleep(1)

            if page in self.page_table:
                print(f"{page} is already in memory.")
                self.page_hits += 1
                self.update_lru(page, hit=True)
            else:
                print(f"{page} is a Page Miss.")
                self.page_faults += 1
                self.update_lru(page, hit=False)

                if None in self.frames:
                    frame_index = self.frames.index(None)
                else:
                    frame_index = self.replace_page()

                virtual_address = f"0x{self.pages.index(page):04X}"
                physical_address = f"0x{random.randint(0x00, 0xFF):02X}"

                self.frames[frame_index] = page
                self.page_table[page] = frame_index
                self.virtual_to_physical_map[page] = (virtual_address, physical_address)
                self.fifo_queue.append(page)

                algo_used = self.replacement_history[-1] if self.replacement_history else "No Replacement Needed"
                self.allocation_table.append(
                    [page, frame_index, algo_used, virtual_address, physical_address]
                )

                print(f"Allocated {page} to Frame {frame_index}. Virtual Address: {virtual_address}, Physical Address: {physical_address} using {algo_used}.")

            self.visualize_allocation(page, frame_index, virtual_address, physical_address, algo_used)
            self.visualize_frame_state()

            try:
                input("Press Enter to continue to the next page...")
            except (EOFError, OSError):
                print("Skipping input wait due to environment limitations.")

        print("\nReconstruction Complete. Data is back in its full form.")
        self.visualize_final_state()
        self.visualize_statistics()

    def replace_page(self):
        algo = REPLACEMENT_ALGORITHMS[self.replacement_algo_index]
        self.replacement_algo_index = (self.replacement_algo_index + 1) % len(REPLACEMENT_ALGORITHMS)

        if algo == "FIFO":
            while self.fifo_queue:
                replaced_page = self.fifo_queue.pop(0)
                if replaced_page in self.page_table:
                    break
        elif algo == "Optimal":
            replaced_page = self.find_optimal_page()
        elif algo == "LRU":
            while self.lru_stack:
                replaced_page = self.lru_stack.pop(0)
                if replaced_page in self.page_table:
                    break

        frame_index = self.page_table.pop(replaced_page, None)
        if frame_index is None:
            raise ValueError(f"Attempted to replace a page that is not in the page table: {replaced_page}")

        self.replacement_history.append(algo)
        print(f"Replaced {replaced_page} from Frame {frame_index} using {algo}.")
        return frame_index

    def find_optimal_page(self):
        future_references = REFERENCE_STRING[REFERENCE_STRING.index(self.pages.index(self.frames[0])) + 1 :]
        max_distance = -1
        page_to_replace = None

        for frame_page in self.frames:
            if frame_page not in self.page_table:
                continue

            try:
                next_use = future_references.index(self.pages.index(frame_page))
            except ValueError:
                next_use = float("inf")

            if next_use > max_distance:
                max_distance = next_use
                page_to_replace = frame_page

        return page_to_replace

    def update_lru(self, page, hit=False):
        if hit:
            if page in self.lru_stack:
                self.lru_stack.remove(page)
            else:
                print(f"Page {page} not found in LRU stack.")
        else:
            if page in self.lru_stack:
                self.lru_stack.remove(page)
            self.lru_stack.append(page)

    def visualize_initial_pages(self):
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, NUM_PAGES + 1)
        ax.set_title("Initial Pages Loaded from Data", fontsize=16)
        ax.set_xlabel("Pages", fontsize=14)
        ax.set_ylabel("Page Index", fontsize=14)
        for i in range(NUM_PAGES):
            ax.add_patch(patches.Rectangle((1, i), 8, 1, fill=False, edgecolor="black", lw=1.5))
            ax.text(5, i + 0.5, self.pages[i], ha="center", va="center", fontsize=12)
        plt.tight_layout()
        plt.show()

    def visualize_allocation(self, page, frame_index, virtual_address, physical_address, algo_used):
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, NUM_FRAMES + 1)
        ax.set_title(f"Allocation with {algo_used} Replacement", fontsize=16)
        ax.set_xlabel("Frames", fontsize=14)
        ax.set_ylabel("Frame Index", fontsize=14)
        for i in range(NUM_FRAMES):
            ax.add_patch(patches.Rectangle((1, i), 8, 1, fill=False, edgecolor="black", lw=1.5))
            content = self.frames[i] if self.frames[i] else "Empty"
            ax.text(5, i + 0.5, content, ha="center", va="center", fontsize=12)
        ax.add_patch(patches.Rectangle((1, frame_index), 8, 1, fill=True, edgecolor="red", alpha=0.2))
        ax.annotate(
            f"Allocating {page}\nVA: {virtual_address}, PA: {physical_address}",
            xy=(5, frame_index + 0.5),
            xytext=(5, NUM_FRAMES + 0.5),
            arrowprops=dict(facecolor="blue"),
            ha="center",
        )
        plt.tight_layout()
        plt.show()

    def visualize_frame_state(self):
        frame_state_table = []
        for i, frame in enumerate(self.frames):
            page = frame if frame else "Empty"
            frame_state_table.append([f"Frame {i}", page])

        fig, ax = plt.subplots(figsize=(8, 6))
        col_labels = ["Frame", "Page"]
        table = plt.table(cellText=frame_state_table, colLabels=col_labels, loc="center", cellLoc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.5, 1.5)
        ax.axis("off")
        ax.set_title("Current Frame State", fontsize=14)
        plt.tight_layout()
        plt.show()

    def visualize_final_state(self):
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, NUM_FRAMES + 2)
        ax.set_title("Final Allocation Table", fontsize=16)
        ax.set_xlabel("Frames", fontsize=14)
        ax.set_ylabel("Frame Index", fontsize=14)

        col_labels = ["Page", "Frame", "Method", "Virtual Address", "Physical Address"]
        table_data = self.allocation_table
        table = plt.table(
            cellText=table_data,
            colLabels=col_labels,
            loc="center",
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.5, 1.5)
        plt.axis("off")
        plt.tight_layout()
        plt.show()

    def visualize_statistics(self):
        labels = ['Page Faults', 'Page Hits']
        values = [self.page_faults, self.page_hits]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(labels, values, color=['red', 'green'])
        ax.set_title('Page Faults vs. Page Hits', fontsize=16)
        ax.set_ylabel('Count', fontsize=14)

        plt.tight_layout()
        plt.show()

        fault_hit_ratio = self.page_faults / (self.page_hits + 1e-6)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(['Fault-to-Hit Ratio'], [fault_hit_ratio], color='blue')
        ax.set_title('Fault-to-Hit Ratio', fontsize=16)
        ax.set_ylabel('Ratio', fontsize=14)

        plt.tight_layout()
        plt.show()

# Main Code
if __name__ == "__main__":
    print("Virtual Memory Manager Visualization")
    print("Initializing...")
    time.sleep(1)

    vmm = VirtualMemoryManager()
    vmm.allocate()
