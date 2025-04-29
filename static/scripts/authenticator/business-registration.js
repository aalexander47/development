function switchTab() {
    const currentTab = document.querySelector("input[name='form-tab']:checked");
    const tabContainers = document.querySelectorAll(".tab-container");
    tabContainers.forEach((tab) => {
      if (!tab.classList.contains("d-none")) {
        tab.classList.add("d-none");
      }
      if (tab.id === `${currentTab.id}-tab`) {
        tab.classList.remove("d-none");
      }
    });
}