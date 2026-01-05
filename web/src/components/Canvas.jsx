import "./canvas.css"
import { Component } from "react";
import Point from "./Point";
import Tooltip from "./Tooltip";

class Canvas extends Component {
  constructor(props) {
    super(props);
    this.state = {
      toolTipImageUrl: null,
    };
  }

  keyPressListener = (e) => {
    if (e.code === "ControlLeft") {
      document.getElementById("canvas").style.cursor = "crosshair";
    }
  };

  keyUpListener = (e) => {
    document.getElementById("canvas").style.cursor = "grab";
  };

  handleMouseEnter = (e) => {
    document.addEventListener("keydown", this.keyPressListener);
    document.addEventListener("keyup", this.keyUpListener);
  };

  handleMouseLeave = (e) => {
    document.removeEventListener("keydown", this.keyPressListener);
    document.removeEventListener("keyup", this.keyUpListener);
  };

  getRowIndexById = (id) => {
    const { originalDataSet } = this.props;
    const ids = originalDataSet?.id;
    if (!ids) return -1;
    // Ensure number comparison if ids are numbers
    return ids.findIndex((x) => Number(x) === Number(id));
  };

  setToolTipImageFromLocalFiles = async (imageID) => {
    if (!imageID) return;

    // const { imageFileMap } = this.state;
    const { originalDataSet, imageFileMap } = this.props;

    if (!originalDataSet || !imageFileMap) return;

    const rowIdx = this.getRowIndexById(imageID);
    if (rowIdx < 0) {
      console.warn("Image ID not found in dataset:", imageID);
      return;
    }

    const imagePathFromCsv = originalDataSet.image_file?.[rowIdx];
    if (!imagePathFromCsv) return;

    // IMPORTANT: CSV path must match how you keyed files.
    // Best practice: store relative paths in CSV (e.g. "images/cat.png"), not absolute OS paths.
    const normalized = String(imagePathFromCsv).replaceAll("\\", "/");

    const file =
      imageFileMap.get(normalized) ||
      imageFileMap.get(normalized.split("/").pop()); // basename fallback

    if (!file) {
      console.warn("No matching uploaded file for path:", normalized);
      return;
    }

    const url = URL.createObjectURL(file);

    // Clean up previous blob URL to avoid leaks
    const prev = this.state.toolTipImageUrl;
    if (typeof prev === "string" && prev.startsWith("blob:")) {
      URL.revokeObjectURL(prev);
    }

    this.setState({ toolTipImageUrl: url });
  };

  render() {
    const { pointSize, displayDataSet } = this.props;
    const { toolTipImageUrl } = this.state;
    if (displayDataSet) {
      return (
        <div
          id="canvas"
          onMouseEnter={this.handleMouseEnter}
          onMouseLeave={this.handleMouseLeave}
        >
          {displayDataSet.map((pointData) => {
            const { id, x, y, thumbnail } = pointData;
            return (
              <Point
              actionFnct={this.setToolTipImageFromLocalFiles}
              key={id}
              xPos={x}
              yPos={y}
              size={pointSize}
              id={id}
              thumbnail={thumbnail}
              />
            );
          })}
          <Tooltip imageURL={toolTipImageUrl} />
        </div>
      );
    } else {
      return <div id="canvas"></div>;
    }
  }
}

export default Canvas;
