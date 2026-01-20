using UnityEngine;

public class MissionStateManager : MonoBehaviour
{
    public static MissionStateManager Instance;
    void Awake()
    {
        if (Instance == null)
        {
            Instance=this;
            DontDestroyOnLoad(gameObject);

        }
        else
        {
            Destroy(gameObject);
        }
    }
    public void SaveMissionState(MissionState state)
    {
        string json=JsonUtility.ToJson(state);
        PlayerPrefs.SetString("TODAY_MISSION",json);
        PlayerPrefs.Save();
    }
    public MissionState LoadMissionState()
    {
        if (!PlayerPrefs.HasKey("TODAY_MISSION"))
        {
            return null;

        }
        string json=PlayerPrefs.GetString("TODAY_MISSION");
        return JsonUtility.FromJson<MissionState>(json);
    }
}
