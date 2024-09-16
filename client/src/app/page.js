"use client";
import { v4 as uuid, v4 } from "uuid";
import styles from "./page.module.css";
import React, { useState, useEffect } from "react";
import ReactPlayer from "react-player";
import Script from "next/script";
import Image from "next/image";
import BarLoader from "react-spinners/BarLoader";


function App() {

  const maxFileSize = process.env.MAX_FILE_SIZE;
  const videoEditorApiUrl = process.env.NEXT_PUBLIC_VIDEO_EDITOR_API_URL
  const awsSDK = process.env.NEXT_PUBLIC_AWS_SDK
  const videoS3BucketName = process.env.NEXT_PUBLIC_S3_VIDEO_BUCKET_NAME
  const awsRegion = process.env.NEXT_PUBLIC_S3_VIDEO_BUCKET_REGION
  const awsIdentityPoolId = process.env.NEXT_PUBLIC_AWS_IDENTITY_POOL_ID

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState();
  const [fileExtension, setFileExtension] = useState();
  const [file, setFile] = useState();
  const [fileName, setFileName] = useState();
  const [fileUrl, setFileUrl] = useState();
  const [fileKey, setOriginalFileKey] = useState();
  const [watermarkUrl, setWatermarkUrl] = useState();
  const [watermarkTransparency, setWatermarkTransparency] = useState();
  const [watermarkLocation, setWatermarkLocation] = useState("Centered");

  const [start, setStart] = useState();
  const [end, setEnd] = useState();
  const [form, setForm] = useState();




  const handleUpload = (e) => {
    e.preventDefault();
    console.log("hi", process.env.NODE_ENV, process.env.NEXT_PUBLIC_VIDEO_EDITOR_API_URL)

    if ((typeof file == 'undefined')) {
      setError("No file was selected"); 
      return
    } 
    if ((typeof file !== 'undefined')) {
      if (file.size > maxFileSize) {
        setError(`Max file size is ${maxFileSize}. This file is ${file.size}`); 
        return

      }
    }


    console.log(
      "State pre S3 upload\n",
      "originalUploadFile :" + file,
      "fileExtension :" + fileExtension,
      "fileUrl :" + fileUrl,
      "originalUploadFileKey :" + fileKey
    );
    typeof fileExtension;
    var bucketName = videoS3BucketName;
    var bucketRegion = awsRegion;
    var IdentityPoolId = awsIdentityPoolId;
    AWS.config.update({
      region: bucketRegion,
      credentials: new AWS.CognitoIdentityCredentials({
        IdentityPoolId: IdentityPoolId,
      }),
    });

    var s3 = new AWS.S3({
      apiVersion: "2006-03-01",
      params: { Bucket: bucketName },
    });

    var key = uuid() + "/" + file.name;

    s3.upload(
      {
        Key: key,
        Body: file,
      },
      function (err, data) {
        if (err) {
          setError(err)
          // maybe remove
          console.log("s3 upload response data", data);
        } else {
          console.log("s3 upload response data", data);
          setOriginalFileKey(data.Key);
          setFileExtension(data.Key.split(".")[1].toLowerCase());
          setFileUrl(data.Location);
          setFileName(data.Key.split("/")[1].toLowerCase())
        }
      }
    );
  };

  const handleVideoProcessing = (e) => {
    e.preventDefault();
    console.log(
      "State pre video processing\n",
      "originalUploadFile :" + file,
      "fileExtension :" + fileExtension,
      "fileUrl :" + fileUrl,
      "originalUploadFileKey :" + fileKey
    );

    var requestBody = "";
    var url = "";

    if (form == "videoTrim") {
      url = `${videoEditorApiUrl}/videoTrim`;
      requestBody = JSON.stringify({
        fileUrl: fileUrl,
        fileKey: fileKey,
        start: start,
        end: end,
      });
    }

    if (form == "videoToGIF") {
      url = `${videoEditorApiUrl}/videoToGIF`; 
      requestBody = JSON.stringify({
        fileUrl: fileUrl,
        fileKey: fileKey,
      });
    }

    if (form == "GIFToVideo") {
      url = `${videoEditorApiUrl}/GIFToVideo`;
      requestBody = JSON.stringify({
        fileUrl: fileUrl,
        fileKey: fileKey,
      });
    }

    if (form == "watermark") {
      url = `${videoEditorApiUrl}/watermark`;
      requestBody = JSON.stringify({
        fileUrl: fileUrl,
        fileKey: fileKey,
        watermarkUrl: watermarkUrl,
        watermarkTransparency: watermarkTransparency,
        watermarkLocation: watermarkLocation,
      });
    }


    if (form == "removeAudio") {
      url = `${videoEditorApiUrl}/removeAudio`;
      requestBody = JSON.stringify({
        fileUrl: fileUrl,
        fileKey: fileKey,
      });
    }

    if (form == "extractAudio") {
      url = `${videoEditorApiUrl}/extractAudio`;
      requestBody = JSON.stringify({
        fileUrl: fileUrl,
        fileKey: fileKey,
      });
    }

    console.log("request data", requestBody);
    setLoading(true);
    fetch(url, {
      method: "POST",
      body: requestBody,
      headers: { "Content-Type": "application/json" },
    })
      .then((response) => {
        return response.json(); // return promise
      })
      .then((data) => {
        
        if (data.message) {
          setLoading(false);
          setError(data.message)
          // maybe remove
          console.log("response data", data);

        } else {
          setLoading(false);
          console.log("response data", data);
          setFileExtension(data.fileExtension);
          setFileUrl(data.fileUrl);
          setFileName(data.fileName)
        }
      })
      .catch((err) => setError(err.message) );
  };

  // useEffect(() => {
  //   // UPDATE local file details
  //   console.log("State post video processing\n", file, fileUrl, fileKey);

  // }, [fileUrl]);

  const handleChange = (e) => {
    console.log();

    setFile(e.target.files[0]);
    setFileExtension(e.target.files[0].type.toLowerCase());
  };

  const startInputHandler = (e) => {
    setStart(e.target.value);
  };

  const endInputHandler = (e) => {
    setEnd(e.target.value);
  };

  const watermarkInputHandler = (e) => {
    setWatermarkUrl(e.target.value);
  };

  const watermarkTransparencyHandler = (e) => {
    setWatermarkTransparency(e.target.value);
  };

  const watermarkLocationHandler = (e) => {
    setWatermarkLocation(e.target.value);
  };

  const handleFormChange = (formType) => {
    setForm(formType);
  };

  let displayForm;

  if (form == "videoTrim") {
    displayForm = (
      <div>
        <input
          onChange={startInputHandler}
          type="text"
          value={start}
          placeholder="Starting HH:MM:SS"
        />
        <input
          onChange={endInputHandler}
          type="text"
          value={end}
          placeholder="Ending HH:MM:SS"
        />
        <button onClick={handleVideoProcessing}>Trim Video</button>
      </div>
    );
  }
  if (form == "videoToGIF") {
    displayForm = (
      <div>
        <button onClick={handleVideoProcessing}>Convert Video to GIF</button>
      </div>
    );
  }

  if (form == "GIFToVideo") {
    displayForm = (
      <div>
        <button onClick={handleVideoProcessing}>Convert GIF to Video</button>
      </div>
    );
  }

  if (form == "watermark") {
    displayForm = (
      <div>
        <div>
          <label>Watermark Logo: </label>
          <input
            onChange={watermarkInputHandler}
            type="url"
            value={watermarkUrl}
            placeholder="URL to image"
          />
        </div>
        <div>
          <label>Set Transparency: </label>
          <input
            onChange={watermarkTransparencyHandler}
            type="text"
            value={watermarkTransparency}
            placeholder="0 is most, 100 is least"
          />
        </div>

        <div>
          <label>Choose location: </label>
          <select
            onChange={watermarkLocationHandler}
            name="locations"
            id="locations"
          >
            <option value="Centered">Centered</option>
            <option value="Top Left">Top Left</option>
            <option value="Top Right">Top Right</option>
            <option value="Bottom Left">Bottom Left</option>
            <option value="Bottom Right">Bottom Right</option>
          </select>
        </div>

        <button onClick={handleVideoProcessing}>Add Watermark</button>
      </div>
    );
  }

  if (form == "removeAudio") {
    displayForm = (
      <div>
        <button onClick={handleVideoProcessing}>Remove All Audio</button>
      </div>
    );
  }

  if (form == "extractAudio") {
    displayForm = (
      <div>
        <button onClick={handleVideoProcessing}>Extract Audio</button>
      </div>
    );
  }
  // if (file) {
  //   fileName = file.name;
  // }
  // if (fileUrl) {
  //   fileName = fileKey.split("/")[1];
  // }
  let spinner = <BarLoader width="400px" color="#36d7b7" />;

  let modal = (
    <>
    <div className={styles.backdrop} onClick = {() => setError()}></div>
    <div
      className={styles.modal}
      style={{
        transform: error ? "translateY(0)" : "translateY(-100vh)",
        opacity: error ? "1" : "0",
      }}
    >
      {error ? error : null}
    </div>
    </>
  );

  return (
    <>

      <Script
        src={awsSDK}
        async
      ></Script>
      {error ? modal : null}
      <main className={styles.main}>
        <div className={styles.description}>
          <p>
            Simple video and GIF editing for free. Get started by selecting a
            file&nbsp;
          </p>
        </div>

        <div className={styles.player}>
          <div className={styles.fileInput}>
            <input
              onChange={handleChange}
              type="file"
              id="file"
              className={styles.file}
            />
            <label htmlFor="file">Select File</label>
          </div>
          <div>{fileName ? fileName : "Upload a file"}</div>
          <div>
            <button onClick={handleUpload}> Upload </button>
          </div>
          <div className={styles.spinner}>{loading ? spinner : null}</div>

          {fileUrl && !loading ? (
            <div>
              {fileExtension == "gif" ? (
                <a
                  download={fileKey.split("/")[1]}
                  href={fileUrl}
                  title={fileKey.split("/")[1]}
                >
                  <img
                    src={fileUrl}
                    height="160"
                    width="240"
                    alt="loading..."
                  />
                </a>
              ) : (
                <ReactPlayer
                  width="460px"
                  height="300px"
                  controls={true}
                  url={fileUrl}
                />
              )}

              {displayForm}
            </div>
          ) : null}
        </div>

        <div className={styles.grid}>
          <button
            onClick={() => handleFormChange("videoTrim")}
            className={
              form == "videoTrim" ? styles.card + styles.selected : styles.card
            }
          >
            <h2>Video Trim</h2>
          </button>

          <button
            onClick={() => handleFormChange("videoToGIF")}
            value={"videoToGIF"}
            className={
              form == "videoToGIF" ? styles.card + styles.selected : styles.card
            }
          >
            <h2>Video to GIF</h2>
          </button>

          <button
            onClick={() => handleFormChange("GIFToVideo")}
            value={"GIFToVideo"}
            className={
              form == "GIFToVideo" ? styles.card + styles.selected : styles.card
            }
          >
            <h2>GIF to Video</h2>
          </button>
          <button
            onClick={() => handleFormChange("watermark")}
            value={"watermark"}
            className={
              form == "watermark" ? styles.card + styles.selected : styles.card
            }
          >
            <h2>Watermark</h2>
          </button>

          <button
            onClick={() => handleFormChange("removeAudio")}
            value={"removeAudio"}
            className={
              form == "removeAudio" ? styles.card + styles.selected : styles.card
            }
          >
            <h2>Remove Audio</h2>
          </button>

          <button
            onClick={() => handleFormChange("extractAudio")}
            value={"extractAudio"}
            className={
              form == "extractAudio" ? styles.card + styles.selected : styles.card
            }
          >
            <h2>Extract Audio</h2>
          </button>
        </div>
      </main>
    </>
  );
}

export default App;
